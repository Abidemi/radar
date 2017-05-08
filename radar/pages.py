from enum import Enum


class PAGE(Enum):
    ADDRESSES = 'ADDRESSES'
    ALIASES = 'ALIASES'
    ALPORT_CLINICAL_PICTURES = 'ALPORT_CLINICAL_PICTURES'
    COHORTS = 'COHORTS'
    CONSULTANTS = 'CONSULTANTS'
    DEMOGRAPHICS = 'DEMOGRAPHICS'
    DIAGNOSES = 'DIAGNOSES'
    DIALYSIS = 'DIALYSIS'
    FAMILY_HISTORY = 'FAMILY_HISTORY'
    FETAL_ANOMALY_SCANS = 'FETAL_ANOMALY_SCANS'
    FETAL_ULTRASOUNDS = 'FETAL_ULTRASOUNDS'
    FUAN_CLINICAL_PICTURES = 'FUAN_CLINICAL_PICTURES'
    GENETICS = 'GENETICS'
    HNF1B_CLINICAL_PICTURES = 'HNF1B_CLINICAL_PICTURES'
    HOSPITALISATIONS = 'HOSPITALISATIONS'
    HOSPITALS = 'HOSPITALS'
    INDIA_ETHNICITIES = 'INDIA_ETHNICITIES'
    INS_CLINICAL_PICTURES = 'INS_CLINICAL_PICTURES'
    INS_RELAPSES = 'INS_RELAPSES'
    LIVER_DISEASES = 'LIVER_DISEASES'
    LIVER_IMAGING = 'LIVER_IMAGING'
    LIVER_TRANSPLANTS = 'LIVER_TRANSPLANTS'
    MEDICATIONS = 'MEDICATIONS'
    META = 'META'
    MPGN_CLINICAL_PICTURES = 'MPGN_CLINICAL_PICTURES'
    NEPHRECTOMIES = 'NEPHRECTOMIES'
    NUMBERS = 'NUMBERS'
    NUTRITION = 'NUTRITION'
    QUESTIONNAIRES = 'QUESTIONNAIRES'
    PATHOLOGY = 'PATHOLOGY'
    PLASMAPHERESIS = 'PLASMAPHERESIS'
    PREGNANCIES = 'PREGNANCIES'
    PRIMARY_DIAGNOSIS = 'PRIMARY_DIAGNOSIS'
    RENAL_IMAGING = 'RENAL_IMAGING'
    RENAL_PROGRESSION = 'RENAL_PROGRESSION'
    RESULTS = 'RESULTS'
    SALT_WASTING_CLINICAL_FEATURES = 'SALT_WASTING_CLINICAL_FEATURES'
    TRANSPLANTS = 'TRANSPLANTS'

    def __str__(self):
        return str(self.value)
