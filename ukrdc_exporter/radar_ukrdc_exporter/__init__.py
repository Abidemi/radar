__version__ = '0.1'

import logging
import requests
from flask import Flask
from celery import Celery, chain

from radar.database import db
from radar.models.patients import Patient, GENDERS
from radar.models.patient_aliases import PatientAlias
from radar.models.patient_addresses import PatientAddress
from radar.models.patient_numbers import PatientNumber
from radar.models.groups import (
    GROUP_CODE_NHS,
    GROUP_CODE_CHI,
    GROUP_CODE_HANDC,
    GROUP_TYPE
)


logger = logging.getLogger(__name__)

NATIONAL_IDENTIFIERS = [
    GROUP_CODE_NHS,
    GROUP_CODE_CHI,
    GROUP_CODE_HANDC
]


def create_app():
    app = Flask(__name__)
    app.config.from_envvar('RADAR_SETTINGS')

    # noinspection PyUnresolvedReferences
    from radar import models  # noqa

    db.init_app(app)

    return app


def create_celery():
    app = create_app()

    celery = Celery(app.import_name)
    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery


celery = create_celery()


def get_patient(patient_id):
    return Patient.query.get(patient_id)


def export_name(sda_patient, patient):
    if patient.first_name or patient.last_name:
        sda_name = sda_patient['name'] = dict()

        if patient.first_name:
            sda_name['given_name'] = patient.first_name

        if patient.last_name:
            sda_name['family_name'] = patient.last_name


def export_date_birth(sda_patient, patient):
    if patient.date_of_birth:
        sda_patient['date_birth'] = patient.date_of_birth


def export_date_death(sda_patient, patient):
    if patient.date_of_death:
        sda_patient['date_death'] = patient.date_of_death


def export_gender(sda_patient, patient):
    if patient.gender is not None:
        gender = patient.gender
        description = GENDERS.get(gender)

        if description is None:
            logger.error('Unknown gender={}'.format(gender))
            return

        code = str(gender)

        sda_patient['gender'] = {
            'code': code,
            'description': description
        }


def export_contact_info(sda_patient, patient):
    if (
        patient.home_number or
        patient.work_number or
        patient.mobile_number or
        patient.email_address
    ):
        sda_contact_info = sda_patient['contact_info'] = dict()

        if patient.home_number:
            sda_contact_info['home_phone_number'] = patient.home_number

        if patient.work_number:
            sda_contact_info['work_phone_number'] = patient.work_number

        if patient.mobile_number:
            sda_contact_info['mobile_phone_number'] = patient.mobile_number

        if patient.email_address:
            sda_contact_info['email_address'] = patient.email_address


def export_aliases(sda_patient, patient):
    q = PatientAlias.query
    q = q.filter(PatientAlias.patient == patient)
    q = q.filter(PatientAlias.source_type == 'RADAR')
    aliases = q.all()

    if len(aliases) == 0:
        return

    sda_aliases = sda_patient.setdefault('aliases', list())

    for alias in aliases:
        if not alias.first_name and not alias.last_name:
            continue

        sda_name = {}

        if alias.first_name:
            sda_name['given_name'] = alias.first_name

        if alias.last_name:
            sda_name['family_name'] = alias.last_name

        sda_aliases.append(sda_name)


def export_addresses(sda_patient, patient):
    q = PatientAddress.query
    q = q.filter(PatientAddress.patient == patient)
    q = q.filter(PatientAddress.source_type == 'RADAR')
    addresses = q.all()

    if len(addresses) == 0:
        return

    sda_addresses = sda_patient.setdefault('addresses', list())

    for address in addresses:
        lines = [
            address.address_1, address.address_2,
            address.address_3, address.address_4
        ]

        street = '; '.join(line for line in lines if line)

        if not street and not address.postcode:
            continue

        sda_address = dict()

        if street:
            sda_address['street'] = street

        if address.postcode:
            sda_address['zip'] = {
                'code': address.postcode,
                'description': address.postcode,
            }

        sda_addresses.append(sda_address)


def export_patient_numbers(sda_patient, patient):
    q = PatientNumber.query
    q = q.filter(PatientNumber.patient == patient)
    q = q.filter(PatientNumber.source_type == 'RADAR')
    patient_numbers = q.all()

    sda_patient_numbers = sda_patient.setdefault('patient_numbers', list())

    sda_patient_number = {
        'number': str(patient.id),
        'number_type': 'MRN',
        'organization': {
            'code': 'RADAR',
            'description': 'RaDaR'
        }
    }

    sda_patient_numbers.append(sda_patient_number)

    for patient_number in patient_numbers:
        if patient_number.number_group.type == GROUP_TYPE.OTHER and patient_number.number_group.code in NATIONAL_IDENTIFIERS:
            number_type = 'NI'
        else:
            number_type = 'MRN'

        sda_patient_number = {
            'number': patient_number.number,
            'number_type': number_type,
            'organization': {
                'code': patient_number.number_group.code,
                'description': patient_number.number_group.name
            }
        }

        sda_patient_numbers.append(sda_patient_number)


def export_patient(sda_container, patient):
    sda_patient = sda_container.setdefault('patient', dict())
    export_name(sda_patient, patient)
    export_date_birth(sda_patient, patient)
    export_date_death(sda_patient, patient)
    export_gender(sda_patient, patient)
    export_contact_info(sda_patient, patient)
    export_aliases(sda_patient, patient)
    export_addresses(sda_patient, patient)
    export_patient_numbers(sda_patient, patient)


@celery.task
def export_sda(patient_id):
    patient = get_patient(patient_id)

    if patient is None:
        logger.error('Patient not found id={id}'.format(id=patient_id))
        return

    sda_container = {}

    export_patient(sda_container, patient)

    # TODO datetime to iso-8601

    return sda_container


@celery.task
def send_to_ukrdc(sda_container):
    # TODO url
    # TODO timeout
    # TODO error handling

    url = ''
    requests.post(url, json=sda_container)


def export_to_ukrdc(patient_id):
    chain(export_sda.s(patient_id), send_to_ukrdc.s())


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        print export_sda(1)
