import argparse
import ConfigParser

from cornflake import fields, serializers
from cornflake.sqlalchemy_orm import ReferenceField
import tablib
import xlsxwriter

from radar.app import Radar
from radar.database import db
from radar.exporter.exporters import exporter_map
from radar.models.groups import Group
from radar.models.users import User

from radar.models import GroupPatient, Patient
from sqlalchemy import and_, or_, text



PATIENTS = ('id', 'patient_number', 'first_name', 'last_name', 'date_of_birth', 'date_of_death', 'gender', 'ethnicity', 'recruited_date', 'recruited_hospital', 'recruited_user')
PATIENT_DEMOGRAPHICS = ('patient_id', 'source_group', 'first_name', 'last_name', 'date_of_birth', 'date_of_death', 'gender', 'ethnicity', 'home_number', 'work_number', 'mobile_number', 'email_address', 'created_date', 'created_user', 'modified_date', 'modified_user')


class Basic(object):
    __sheetname__ = 'patients'

    def __init__(self, patient):
        self.id = patient.id
        self.patient_number = patient.primary_patient_number.number
        self.first_name = patient.first_name
        self.last_name = patient.last_name
        self.ethnicity = patient.ethnicity.label if patient.ethnicity else None
        self.ukrdc = True if patient.ukrdc else False

    def is_value_missing(self, prop):
        return bool(getattr(self, prop))

    @property
    def header(self):
        return ('id', 'number', 'first_name', 'last_name', 'ethnicity', 'ukrdc')

    @property
    def data(self):
        return self.id, self.patient_number, self.first_name, self.last_name, self.ethnicity, self.ukrdc

    def export(self, sheet, row=1):
        sheet.write_row(row, 0, (self.id, self.patient_number, self.first_name, self.last_name, self.ethnicity, str(self.ukrdc)))
        return row + 1


class Demographics(object):
    __sheetname__ = 'demographics'

    def __init__(self, patient):
        self.patient_id = patient.id
        self.demographics = patient.patient_demographics

    @property
    def header(self):
        return ('patient_id', 'source_group', 'source_type', 'first_name', 'last_name')

    def export(self, sheet, row=1):
        for demog in self.demographics:
            sheet.write_row(row, 0, (self.patient_id, demog.source_group.name, demog.source_type, demog.first_name, demog.last_name))
            row = row + 1
        return row


class Patient(object):
    __slots__ = ('basic', 'demographics')

    def __init__(self, patient):
        self.basic = Basic(patient)
        self.demographics = Demographics(patient)


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

        workbook = xlsxwriter.Workbook('{}_export.xlsx'.format(self.hospital_code))

        for attr in patient.__slots__:
            obj = getattr(patient, attr)

            sheet = workbook.add_worksheet(obj.__sheetname__)
            sheet.write_row('A1', obj.header)
            current_row = 1
            for patient in self.data:
                current_row = getattr(patient, attr).export(sheet, current_row)






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


def sheet_names(config_parser):
    config = parse_config(config_parser)

    sheets = ['report']

    for name in config_parser.sections():
        if name == 'global':
            continue

        sheets.append(name)
    return sheets


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


def write_patients_header(sheet):
    pass


def export_patients(patient, sheet):
    pass


def export(patient, book, first_run=False):
    sheet = book.get_worksheet_by_name('patients')
    if first_run:
        write_patients_header(sheet)
    export_patients(patient, sheet)



def export_validate(sheets):
    nurtureins = Group.query.filter_by(code='NURTUREINS').first()
    nurtureckd = Group.query.filter_by(code='NURTURECKD').first()
    groups = (nurtureins, nurtureckd)
    hospital_ids = get_hospitals()

    for hospital_id in hospital_ids:
        hospital = Group.query.get(hospital_id)
        # workbook = xlsxwriter.Workbook('{}_export.xlsx'.format(hospital.code))
        # for sheet_name in sheets:
            # workbook.add_worksheet(sheet_name)
        print(hospital_id)
        patient_list = PatientList(hospital.code)
        for p in hospital.patients:
            if (p.in_group(nurtureckd) or p.in_group(nurtureins)) and not p.test:
                patient_list.append(Patient(p))
        patient_list.export()




        # first_run = True
        # for patient in patients:
        #     export(p, workbook, first_run)
        #     first_run = False


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('config')
    argument_parser.add_argument('dest')
    args = argument_parser.parse_args()

    app = Radar()

    config_parser = ConfigParser.ConfigParser()
    config_parser.readfp(open(args.config))
    with app.app_context():
        sheets = sheet_names(config_parser)
        export_validate(sheets)


        # query = db.session.query(GroupPatient, Group, Patient).filter(
        #     and_(
        #         Group.code=='NURTURE',
        #         Patient.test==False,
        #         GroupPatient.group==Group,
        #         GroupPatient.patient==Patient
        #     )
        # )

        # exporters = create_exporters(config_parser)

        # datasets = []

        # # Export data
        # for name, exporter in exporters:
        #     print 'Exporting {0}...'.format(name)
        #     exporter.run()
        #     # patient_list = []
        #     # for p in exporter._query:
        #     #     patient_list = [p for p in exporter._query]

        #     dataset = exporter.dataset

        #     dataset.title = name
        #     datasets.append(dataset)

        # databook = tablib.Databook()

        # for dataset in datasets:
        #     databook.add_sheet(dataset)

        # save(databook, 'xlsx', args.dest)


if __name__ == '__main__':
    main()
