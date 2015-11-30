from sqlalchemy import or_, and_

from radar.auth.sessions import current_user
from radar.database import db
from radar.models.patients import Patient
from radar.models.patient_demographics import PatientDemographics
from radar.patient_search import filter_by_date_of_birth, filter_by_first_name, \
    filter_by_last_name, filter_by_patient_number_at_organisation
from radar.models.cohorts import CohortPatient
from radar.models.patient_numbers import PatientNumber
from radar.organisations import get_nhs_organisation, get_chi_organisation, \
    get_ukrdc_organisation, get_radar_organisation
from radar.cohorts import get_radar_cohort
from radar.data_sources import get_radar_data_source
from radar.models.organisations import OrganisationPatient, Organisation
from radar.models.organisations import ORGANISATION_TYPE_OTHER, ORGANISATION_CODE_NHS, ORGANISATION_CODE_CHI
from radar.validation.utils import validate


def recruit_patient_search(params):
    patients = Patient.query\
        .filter(filter_by_first_name(params['first_name']))\
        .filter(filter_by_last_name(params['last_name']))\
        .filter(filter_by_date_of_birth(params['date_of_birth']))\
        .filter(filter_by_patient_number_at_organisation(params['number'], params['number_organisation']))\
        .all()

    results = []

    for patient in patients:
        result = {
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'date_of_birth': patient.date_of_birth,
            'patient_numbers': [
                {
                    'number': patient.id,
                    'organisation': get_radar_organisation(),
                },
                {
                    'number': params['number'],
                    'organisation': params['number_organisation'],
                }
            ]
        }
        results.append(result)

    return results


def recruit_patient(params):
    radar_id = params.get('radar_id')
    cohort = params['cohort']
    organisation = params['recruited_by_organisation']

    if radar_id:
        patient = Patient.query.get(radar_id)
    else:
        radar_data_source = get_radar_data_source()
        radar_cohort = get_radar_cohort()

        patient = Patient()
        patient.is_active = True
        patient = validate(patient)
        db.session.add(patient)

        radar_cohort_patient = CohortPatient()
        radar_cohort_patient.patient = patient
        radar_cohort_patient.cohort = radar_cohort
        radar_cohort_patient.recruited_by_organisation = organisation
        radar_cohort_patient.is_active = True
        radar_cohort_patient = validate(radar_cohort_patient)
        db.session.add(radar_cohort_patient)

        patient_demographics = PatientDemographics()
        patient_demographics.patient = patient
        patient_demographics.data_source = radar_data_source
        patient_demographics.first_name = params['first_name']
        patient_demographics.last_name = params['last_name']
        patient_demographics.date_of_birth = params['date_of_birth']
        patient_demographics.gender = params['gender']
        patient_demographics.ethnicity = params.get('ethnicityCode')
        patient_demographics = validate(patient_demographics)
        db.session.add(patient_demographics)

        # TODO validation
        for x in params['patient_numbers']:
            patient_number = PatientNumber()
            patient_number.patient = patient
            patient_number.data_source = radar_data_source
            patient_number.organisation = x['organisation']
            patient_number.number = x['number']
            patient_number = validate(patient_number)
            db.session.add(patient_number)

    # Add the patient to the cohort
    if not patient.in_cohort(cohort):
        cohort_patient = CohortPatient()
        cohort_patient.patient = patient
        cohort_patient.cohort = cohort
        cohort_patient.recruited_by_organisation = organisation
        cohort_patient.is_active = True
        cohort_patient = validate(cohort_patient)
        db.session.add(cohort_patient)

    # Add the patient to the organisation
    if not patient.in_organisation(organisation):
        organisation_patient = OrganisationPatient()
        organisation_patient.patient = patient
        organisation_patient.organisation = organisation
        organisation_patient.is_active = True
        organisation_patient = validate(organisation_patient)
        db.session.add(organisation_patient)

    db.session.commit()

    return patient


def filter_patient_number_organisations(query):
    return query.filter(or_(
        and_(Organisation.type == ORGANISATION_TYPE_OTHER, Organisation.code == ORGANISATION_CODE_NHS),
        and_(Organisation.type == ORGANISATION_TYPE_OTHER, Organisation.code == ORGANISATION_CODE_CHI),
    ))
