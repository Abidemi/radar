from sqlalchemy import text

import xlsxwriter

from radar.app import Radar
from radar.database import db

from radar.exporter.utils import get_months, get_years
from radar.models.groups import Group


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


def get_form_data(entry, bounds, fields):
    data = [entry.patient_id]
    for field in fields[bounds]:
        data.append(entry.data.get(field, None))

    data.append(format_date(entry.created_date, long=True))
    data.append(entry.created_user.name)
    data.append(format_date(entry.modified_date, long=True))
    data.append(entry.modified_user.name)
    return data


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
            if not diagnosis.status:
                continue
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
        for entry in self.entries:

            data = get_form_data(entry, slice(1, -4), self.fields)
            sheet.write_row(row, 0, data)
            for col in (1, 2, 3, 4, 5, 6, 7, 9):
                if not data[col]:
                    sheet.write(row, col, data[col], errorfmt)
            if data[7] and not data[8]:
                sheet.write(row, 8, data[8], warningfmt)
            if data[9] and not data[10]:
                sheet.write(row, 10, data[10], warningfmt)

            row = row + 1
        return row


class NurtureCKD(BaseSheet):
    __sheetname__ = 'nurtureckd'

    def __init__(self, entries):
        self.entries = entries
        self.fields = (
            'patient_id',
            'date',
            'visit',
            'vaccinationFlu',
            'vaccinationPneumonia',
            'admission',
            'admissionNumber',
            'admissionEmergency',
            'admissionPlanned',
            'admissionDays',
            'admissionAntibiotics',
            'medicine1',
            'tabletsParacetamol',
            'yearsParacetamol',
            'medicine2',
            'tabletsCocodamol',
            'yearsCocodamol',
            'medicine3',
            'tabletsIbuprofen',
            'yearsIbuprofen',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row, errorfmt, warningfmt):
        for entry in self.entries:

            data = get_form_data(entry, slice(1, -4), self.fields)
            sheet.write_row(row, 0, data)

            row = row + 1
        return row


class FamilyDiseasesHistory(BaseSheet):
    __sheetname__ = 'family-diseases-history'

    def __init__(self, entries):
        self.entries = entries
        self.fields = (
            'patient_id',
            'chd',
            'eskd',
            'diabetes',
            'chdRelative1',
            'chdRelative2',
            'chdRelative3',
            'eskdRelative1',
            'eskdRelative2',
            'eskdRelative3',
            'diabetesRelative1',
            'diabetesRelative2',
            'diabetesRelative3',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row, errorfmt, warningfmt):
        for entry in self.entries:

            data = get_form_data(entry, slice(1, -4), self.fields)
            sheet.write_row(row, 0, data)

            row = row + 1
        return row


class DiabeticComplications(BaseSheet):
    __sheetname__ = 'diabetic-complications'

    def __init__(self, entries, patient):
        self.patient = patient
        self.entries = entries
        self.fields = (
            'patient_id',
            'laser',
            'foot',
            'ulcers',
            'retinopathy',
            'peripheral',
            'neuropathy',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row, errorfmt, warningfmt):
        diagnoses = [diagnosis for diagnosis in self.patient.patient_diagnoses if diagnosis.status]
        interested = set(('Diabetes - Type I', 'Diabetes - Type II'))
        diabetes = [diagnosis for diagnosis in diagnoses if diagnosis.name in interested]
        if diabetes and not self.entries:
            sheet.write(row, 0, self.patient.id, errorfmt)
            row = row + 1

        for entry in self.entries:
            data = get_form_data(entry, slice(1, -4), self.fields)
            sheet.write_row(row, 0, data)
            row = row + 1
        return row


class Anthropometrics(BaseSheet):
    __sheetname__ = 'anthropometrics'

    def __init__(self, entries):
        self.entries = entries
        self.fields = (
            'patient_id',
            'date',
            'height',
            'weight',
            'hip',
            'waist',
            'arm',
            'up',
            'grip',
            'karnofsky',
            'systolic1',
            'systolic2',
            'systolic3',
            'systolic',
            'diastolic1',
            'diastolic2',
            'diastolic3',
            'diastolic',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row, errorfmt, warningfmt):
        for entry in self.entries:

            data = get_form_data(entry, slice(1, -4), self.fields)
            sheet.write_row(row, 0, data)

            for no, item in enumerate(data):
                if not item:
                    sheet.write(row, no, data[no], errorfmt)

            row = row + 1
        return row


class Medications(BaseSheet):
    __sheetname__ = 'medications'

    def __init__(self, medications):
        self.medications = medications
        self.fields = (
            'patient_id',
            'source_group',
            'source_type',
            'from_date',
            'to_date',
            'drug_id',
            'drug',
            'drug_text',
            'dose_quantity',
            'dose_unit',
            'dose_unit_label',
            'dose_text',
            'frequency',
            'route',
            'route_label',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        for instance in self.medications:
            data = [getattr(instance, field) for field in self.fields]
            data[1] = instance.source_group.code

            data[3] = format_date(data[3])
            data[4] = format_date(data[4])

            data[-4] = format_date(data[-4], long=True)
            data[-3] = instance.created_user.name
            data[-2] = format_date(data[-2], long=True)
            data[-1] = instance.modified_user.name

            sheet.write_row(row, 0, data)

            row = row + 1
        return row


class Results(BaseSheet):
    __sheetname__ = 'results'

    def __init__(self, results, observations):
        self.results = results
        self.observations = observations
        self.fields = ['patient_id', 'source_group', 'source_type', 'date']
        self.fields.extend(self.observations)

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        from collections import OrderedDict

        data = OrderedDict()

        for result in self.results:
            key = (result.patient_id, result.source_group.name, result.source_type, result.date)
            if key not in data:
                data[key] = {}

            data[key][result.observation.name] = result.value_label_or_value

        for key, results in data.items():
            data = list(key)
            for test in self.observations:
                data.append(results.get(test, None))

            sheet.write_row(row, 0, data)
            row = row + 1

        return row


class Pathology(BaseSheet):
    __sheetname__ = 'pathology'

    def __init__(self, pathology):
        self.pathology = pathology
        self.fields = (
            'patient_id',
            'source_group',
            'date',
            'kidney_type',
            'kidney_type_label',
            'kidney_side',
            'kidney_side_label',
            'reference_number',
            'image_url',
            'histological_summary',
            'em_findings',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        for instance in self.pathology:
            data = [getattr(instance, field) for field in self.fields]
            data[1] = instance.source_group.code

            data[2] = format_date(data[2])

            data[-4] = format_date(data[-4], long=True)
            data[-3] = instance.created_user.name
            data[-2] = format_date(data[-2], long=True)
            data[-1] = instance.modified_user.name

            sheet.write_row(row, 0, data)

            row = row + 1
        return row


class RenalProgressions(BaseSheet):
    __sheetname__ = 'renal_progressions'

    def __init__(self, progressions):
        self.progressions = progressions
        self.fields = (
            'patient_id',
            'onset_date',
            'ckd3a_date',
            'ckd3b_date',
            'ckd4_date',
            'ckd5_date',
            'esrf_date',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        for instance in self.progressions:
            data = [getattr(instance, field) for field in self.fields]
            data[1] = format_date(data[1])
            data[2] = format_date(data[2])
            data[3] = format_date(data[3])
            data[4] = format_date(data[4])
            data[5] = format_date(data[5])
            data[6] = format_date(data[6])

            data[-4] = format_date(data[-4], long=True)
            data[-3] = instance.created_user.name
            data[-2] = format_date(data[-2], long=True)
            data[-1] = instance.modified_user.name

            sheet.write_row(row, 0, data)

            row = row + 1
        return row


class Dialysis(BaseSheet):
    __sheetname__ = 'dialysis'

    def __init__(self, dialysis):
        self.dialysis = dialysis
        self.fields = (
            'patient_id',
            'source_group',
            'source_type',
            'from_date',
            'to_date',
            'modality',
            'modality_label',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        for instance in self.dialysis:
            data = [getattr(instance, field) for field in self.fields]
            data[1] = instance.source_group.code
            data[3] = format_date(data[3])
            data[4] = format_date(data[4])
            data[-4] = format_date(data[-4], long=True)
            data[-3] = instance.created_user.name
            data[-2] = format_date(data[-2], long=True)
            data[-1] = instance.modified_user.name

            sheet.write_row(row, 0, data)

            row = row + 1
        return row


class Transplants(BaseSheet):
    __sheetname__ = 'transplants'

    def __init__(self, transplants):
        self.transplants = transplants
        self.fields = (
            'patient_id',
            'source_group',
            'source_type',
            'transplant_group',
            'date',
            'modality',
            'modality_label',
            'date_of_recurrence',
            'date_of_failure',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row=1, errorfmt=None, warningfmt=None):
        for instance in self.transplants:
            data = [getattr(instance, field) for field in self.fields]
            data[1] = instance.source_group.code
            data[3] = instance.source_group.code
            data[4] = format_date(data[4])
            data[-4] = format_date(data[-4], long=True)
            data[-3] = instance.created_user.name
            data[-2] = format_date(data[-2], long=True)
            data[-1] = instance.modified_user.name

            sheet.write_row(row, 0, data)

            row = row + 1
        return row


class Samples(BaseSheet):
    __sheetname__ = 'samples'

    def __init__(self, samples):
        self.entries = samples
        self.fields = (
            'patient_id',
            'date',
            'barcode',
            'protocol',
            'visit',
            'edta plasma A',
            'edta plasma B',
            'lihepPlasmaA',
            'lihepPlasmaB',
            'urineC',
            'urineB',
            'urineD',
            'cfUrineB',
            'serumC',
            'serumA',
            'serumB',
            'rna',
            'wholeBlood',
            'created_date',
            'created_user',
            'modified_date',
            'modified_user',
        )

    def export(self, sheet, row, errorfmt, warningfmt):
        for entry in self.entries:

            data = get_form_data(entry, slice(1, -4), self.fields)
            sheet.write_row(row, 0, data)

            row = row + 1
        return row


class Patient(object):
    __sheets__ = (
        'basic',
        'demographics',
        'addresses',
        'aliases',
        'numbers',
        'diagnoses',
        'socioeconomic',

        'nurtureckd',
        'family_diseases_history',
        'diabetic_complications',
        'anthropometrics',
        'medications',
        'results',
        'pathology',
        'renal_progressions',
        'dialysis',
        'transplants',
        'samples',
    )

    def __init__(self, patient):
        self.original_patient = patient
        self.patient_id = patient.id
        self.basic = None
        self.demographics = None
        self.addresses = None
        self.aliases = None
        self.numbers = None
        self.diagnoses = None
        self.socioeconomic = None
        self.nurtureckd = None
        self.family_diseases_history = None
        self.diabetic_complications = None
        self.anthropometrics = None
        self.medications = None
        self.results = None
        self.pathology = None
        self.renal_progressions = None
        self.dialysis = None
        self.transplants = None
        self.samples = None

    def run(self):
        self.basic = Basic(self.original_patient)
        self.demographics = Demographics(self.original_patient)
        self.addresses = Addresses(self.original_patient)
        self.aliases = Aliases(self.original_patient.patient_aliases)
        self.numbers = Numbers(self.original_patient.patient_numbers)
        self.diagnoses = Diagnoses(self.original_patient.patient_diagnoses)
        entries = [entry for entry in self.original_patient.entries if entry.form.slug == 'socio-economic']
        self.socioeconomic = SocioEconomic(entries)
        entries = [entry for entry in self.original_patient.entries if entry.form.slug == 'nurtureckd']
        self.nurtureckd = NurtureCKD(entries)
        entries = [entry for entry in self.original_patient.entries if entry.form.slug == 'family-history']
        self.family_diseases_history = FamilyDiseasesHistory(entries)
        entries = [entry for entry in self.original_patient.entries if entry.form.slug == 'diabetic-complications']
        self.diabetic_complications = DiabeticComplications(entries, self.original_patient)
        entries = [entry for entry in self.original_patient.entries if entry.form.slug == 'anthropometrics']
        self.anthropometrics = Anthropometrics(entries)
        self.medications = Medications(self.original_patient.medications)
        self.results = Results(self.original_patient.results, self.observations)
        self.pathology = Pathology(self.original_patient.pathology)
        self.renal_progressions = RenalProgressions(self.original_patient.renal_progressions)
        self.dialysis = Dialysis(self.original_patient.dialysis)
        self.transplants = Transplants(self.original_patient.transplants)
        self.samples = Samples([entry for entry in self.original_patient.entries if entry.form.slug == 'samples'])

    def add_observations(self, observations):
        self.observations = observations


class PatientList(object):
    def __init__(self, hospital_code):
        self.data = []
        self.hospital_code = hospital_code
        self.observations = set()

    def append(self, patient):
        self.observations |= set([result.observation.name for result in patient.results])
        self.data.append(Patient(patient))

    def export(self):
        try:
            patient = self.data[0]
        except IndexError:
            print('No patients found in {}'.format(self.hospital_code))
            return

        workbook = xlsxwriter.Workbook('{}_export.xlsx'.format(self.hospital_code), {'remove_timezone': True})
        errorfmt = workbook.add_format({'bg_color': 'red'})
        warningfmt = workbook.add_format({'bg_color': 'orange'})

        for patient in self.data:
            patient.add_observations(sorted(self.observations))
            patient.run()

        for attr in patient.__sheets__:
            obj = getattr(patient, attr)

            sheet = workbook.add_worksheet(obj.__sheetname__)
            sheet.write_row('A1', obj.header)
            current_row = 1
            for patient in sorted(self.data, key=lambda pat: pat.patient_id):
                patient.run()
                patient.observations = sorted(self.observations)
                current_row = getattr(patient, attr).export(sheet, current_row, errorfmt, warningfmt)


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
                patient_list.append(p)
        patient_list.export()


def main():
    # argument_parser = argparse.ArgumentParser()
    # argument_parser.add_argument('config')
    # args = argument_parser.parse_args()

    app = Radar()

    # config_parser = ConfigParser.ConfigParser()
    # config_parser.readfp(open(args.config))
    with app.app_context():
        export_validate()


if __name__ == '__main__':
    main()
