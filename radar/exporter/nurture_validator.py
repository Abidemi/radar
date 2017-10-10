import argparse
import ConfigParser

from cornflake import fields, serializers
from cornflake.sqlalchemy_orm import ReferenceField
from sqlalchemy import text

import xlsxwriter

from radar.app import Radar
from radar.database import db
from radar.exporter.exporters import exporter_map
from radar.exporter.utils import get_months, get_years
from radar.models.groups import Group
from radar.models.users import User


DATEFMT = '%d/%m/%Y'
DATETIMEFMT = '%Y-%m-%d %H:%M:%S'


def get_gender(gender_code):
    genders = {0: 'NA', 1: 'M', 2: 'F', 9: 'Not specified'}
    return genders.get(gender_code, 'NA')


def format_date(date, long=False):
    if date and isinstance(date, basestring):
        return date
    if date and long:
        return date.strftime(DATETIMEFMT)
    elif date:
        return date.strftime(DATEFMT)
    return None


class BaseSheet(object):
    def is_value_missing(self, prop):
        return bool(getattr(self, prop))

    @property
    def header(self):
        return self.fields

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_field < len(self.fields):
            self.current_field += 1
            try:
                return str(getattr(self, self.fields[self.current_field - 1]))
            except AttributeError:
                return getattr(self.original_obj, self.fields[self.current_field - 1])
        raise StopIteration

    next = __next__


class Basic(BaseSheet):
    __sheetname__ = 'patients'

    def __init__(self, patient):
        self.original_obj = patient
        self.patient_id = patient.id
        self.patient_number = patient.primary_patient_number.number
        self.ethnicity = patient.ethnicity.label if patient.ethnicity else None
        self.ukrdc = True if patient.ukrdc else False
        self.gender = get_gender(patient.gender)
        self.date_of_birth = format_date(patient.date_of_birth)
        self.date_of_death = format_date(patient.date_of_death)
        self.recruited_date = format_date(patient.recruited_date())
        self.recruited_group = patient.recruited_group().code
        self.recruited_user = patient.recruited_user().name

        self.current_field = 0
        self.fields = (
            'patient_id',
            'patient_number',
            'first_name',
            'last_name',
            'date_of_birth',
            'date_of_death',
            'gender',
            'ethnicity',
            'ukrdc',
            'recruited_date',
            'recruited_group',
            'recruited_user',
        )

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        sheet.write_row(row, 0, self)
        if not self.ethnicity:
            sheet.write(row, 7, (self.ethnicity), errorfmt)
        if not self.ukrdc:
            sheet.write(row, 8, str(self.ukrdc), errorfmt)

        return row + 1


class Demographics(BaseSheet):
    __sheetname__ = 'demographics'

    def __init__(self, patient):
        self.patient_id = patient.id
        self.demographics = patient.patient_demographics
        self.fields = (
            'patient_id',
            'source_group',
            'source_type',
            'first_name',
            'last_name',
            'date_of_birth',
            'date_of_death',
            'gender',
            'ethnicity',
            'home_number',
            'work_number',
            'mobile_number',
            'email_address',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        for demog in self.demographics:
            data = [getattr(demog, field) for field in self.fields]
            data[1] = demog.source_group.code
            data[5] = format_date(data[5])
            data[6] = format_date(data[6])
            data[7] = get_gender(demog.gender)
            data[8] = demog.ethnicity.label if demog.ethnicity else None
            data[13] = format_date(data[13], long=True)
            data[14] = demog.created_user.name
            data[15] = format_date(data[15], long=True)
            data[16] = demog.modified_user.name
            sheet.write_row(row, 0, data)
            if not data[8]:
                sheet.write(row, 8, data[8], errorfmt)

            if not data[12]:
                sheet.write(row, 12, data[12], errorfmt)

            row = row + 1
        return row


class Addresses(BaseSheet):
    __sheetname__ = 'addresses'

    def __init__(self, patient):
        self.addresses = patient.patient_addresses
        self.fields = (
            'patient_id',
            'source_group',
            'source_type',
            'from_date',
            'to_date',
            'address1',
            'address2',
            'address3',
            'address4',
            'postcode',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        for address in self.addresses:
            data = [getattr(address, field) for field in self.fields]
            data[1] = address.source_group.code
            data[3] = format_date(data[3])
            data[4] = format_date(data[4])
            data[10] = format_date(data[10], long=True)
            data[11] = address.created_user.name
            data[12] = format_date(data[12], long=True)
            data[13] = address.modified_user.name
            sheet.write_row(row, 0, data)
            if not data[9]:
                sheet.write(row, 9, data[9], errorfmt)
            row = row + 1

        return row


class Aliases(BaseSheet):
    __sheetname__ = 'aliases'

    def __init__(self, aliases):
        self.aliases = aliases
        self.fields = (
            'patient_id',
            'source_group',
            'source_type',
            'first_name',
            'last_name',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        for alias in self.aliases:
            data = [getattr(alias, field) for field in self.fields]
            data[1] = alias.source_group.code
            data[5] = format_date(data[5], long=True)
            data[6] = alias.created_user.name
            data[7] = format_date(data[7], long=True)
            data[8] = alias.modified_user.name
            sheet.write_row(row, 0, data)
            row = row + 1
        return row


class Numbers(BaseSheet):
    __sheetname__ = 'numbers'

    def __init__(self, numbers):
        self.numbers = numbers
        self.fields = (
            'patient_id',
            'source_group',
            'source_type',
            'number_group',
            'number',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        for number in self.numbers:
            data = [getattr(number, field) for field in self.fields]
            data[1] = number.source_group.code
            data[3] = number.number_group.code
            data[5] = format_date(data[5], long=True)
            data[6] = number.created_user.name
            data[7] = format_date(data[7], long=True)
            data[8] = number.modified_user.name

            sheet.write_row(row, 0, data)

            row = row + 1
        return row


class Diagnoses(BaseSheet):
    __sheetname__ = 'diagnoses'

    def __init__(self, diagnoses):
        self.diagnoses = diagnoses
        self.fields = (
            'patient_id',
            'source_group',
            'source_type',
            'diagnosis',
            'diagnosis_text',
            'symptoms_date',
            'symptoms_age_years',
            'symptoms_age_months',
            'from_date',
            'from_age_years',
            'from_age_months',
            'to_date',
            'to_age_years',
            'to_age_months',
            'gene_test',
            'biochemistry',
            'clinical_picture',
            'biopsy',
            'biopsy_diagnosis',
            'biopsy_diagnosis_label',
            'comments',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        for diagnosis in self.diagnoses:
            data = [getattr(diagnosis, field) for field in self.fields if hasattr(diagnosis, field)]
            data[1] = diagnosis.source_group.code
            data[3] = data[3].name if data[3] else None

            data[5] = format_date(data[5])
            data.insert(6, get_years(diagnosis.symptoms_age))
            data.insert(7, get_months(diagnosis.symptoms_age))

            data[8] = format_date(data[8])
            data.insert(9, get_years(diagnosis.from_age))
            data.insert(10, get_months(diagnosis.from_age))

            data[11] = format_date(data[11])
            data.insert(12, get_years(diagnosis.to_age))
            data.insert(13, get_months(diagnosis.to_age))

            data[21] = format_date(data[21], long=True)
            data[22] = diagnosis.created_user.name
            data[23] = format_date(data[23], long=True)
            data[24] = diagnosis.modified_user.name

            sheet.write_row(row, 0, data)

            if not data[3] and not data[4]:
                sheet.write(row, 3, data[3], errorfmt)
                sheet.write(row, 4, data[4], errorfmt)

            row = row + 1
        return row


class SocioEconomic(BaseSheet):
    __sheetname__ = 'socio-economic'
    def __init__(self, entries):
        self.entries = entries
        self.fields = (
            'patient_id',
            'maritalStatus',
            'education',
            'employmentStatus',
            'firstLanguage',
            'literacy',
            'literacyHelp',
            'smoking',
            'cigarettesPerDay',
            'alcohol',
            'unitsPerWeek',
            'diet',
            'otherDiet',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row, errorfmt, warningfmt):
        pass


class Patient(object):
    __slots__ = ('basic', 'demographics', 'addresses', 'aliases', 'numbers', 'diagnoses', 'socioeconomic')

    def __init__(self, patient):
        self.basic = Basic(patient)
        self.demographics = Demographics(patient)
        self.addresses = Addresses(patient)
        self.aliases = Aliases(patient.patient_aliases)
        self.numbers = Numbers(patient.patient_numbers)
        self.diagnoses = Diagnoses(patient.patient_diagnoses)
        self.socioeconomic = SocioEconomic([entry for entry in patient.entries if entry.form.slug=='socio-economic'])


class PatientList(object):
    def __init__(self, hospital_code):
        self.data = []
        self.hospital_code = hospital_code

    def append(self, patient):
        self.data.append(patient)

    def export(self):
        try:
            patient = self.data[0]
        except IndexError:
            print('No patients found in {}'.format(self.hospital_code))
            return

        workbook = xlsxwriter.Workbook('{}_export.xlsx'.format(self.hospital_code), {'remove_timezone': True})
        errorfmt = workbook.add_format({'bg_color': 'red'})
        warningfmt = workbook.add_format({'bg_color': 'yello'})

        for attr in patient.__slots__:
            obj = getattr(patient, attr)

            sheet = workbook.add_worksheet(obj.__sheetname__)
            sheet.write_row('A1', obj.header)
            current_row = 1
            for patient in sorted(self.data, key=lambda pat: pat.basic.patient_id):
                current_row = getattr(patient, attr).export(sheet, current_row, errorfmt, warningfmt)


def save(data, format, dest):
    with open(dest, 'wb') as f:
        data = data.export(format)
        f.write(data)


class GroupField(ReferenceField):
    model_class = Group


class UserField(ReferenceField):
    model_class = User


class ConfigSerializer(serializers.Serializer):
    anonymised = fields.BooleanField(required=False)
    data_group = GroupField(required=False)
    patient_group = GroupField(required=False)
    user = UserField(required=False)


def parse_config(config_parser):
    if config_parser.has_section('global'):
        data = dict(config_parser.items('global'))
    else:
        data = dict()

    serializer = ConfigSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    return validated_data


def create_exporters(config_parser):
    config = parse_config(config_parser)

    exporters = []

    for name in config_parser.sections():
        if name == 'global':
            continue

        exporter_class = exporter_map[name]

        data = dict(config_parser.items(name))
        exporter_config = exporter_class.parse_config(data)
        exporter_config = dict(
            config.items() +
            exporter_config.items()
        )
        exporter_config.update({'name': name})
        exporter = exporter_class(exporter_config)
        exporters.append((name, exporter))

    return exporters


def get_hospitals():
    select_stmt = text('''
        SELECT DISTINCT created_group_id FROM group_patients
        WHERE group_id IN (
            SELECT id FROM groups
            WHERE code = 'NURTUREINS' OR code = 'NURTURECKD'
        )
    ''')
    results = db.session.execute(select_stmt)
    return [row for row, in results]


def export_validate():
    nurtureins = Group.query.filter_by(code='NURTUREINS').first()
    nurtureckd = Group.query.filter_by(code='NURTURECKD').first()
    hospital_ids = get_hospitals()

    for hospital_id in hospital_ids:
        hospital = Group.query.get(hospital_id)

        print(hospital_id)

        patient_list = PatientList(hospital.code)
        for p in hospital.patients:
            if (p.in_group(nurtureckd) or p.in_group(nurtureins)) and not p.test:
                patient_list.append(Patient(p))
        patient_list.export()


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('config')
    args = argument_parser.parse_args()

    app = Radar()

    config_parser = ConfigParser.ConfigParser()
    config_parser.readfp(open(args.config))
    with app.app_context():
        export_validate()


if __name__ == '__main__':
    main()
