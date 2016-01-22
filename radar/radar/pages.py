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
    HNF1B_CLINICAL_PICTURES = 'HNF1B_CLINICAL_PICTURES'
    GENETICS = 'GENETICS'
    HOSPITALISATIONS = 'HOSPITALISATIONS'
    INS_CLINICAL_PICTURES = 'INS_CLINICAL_PICTURES'
    INS_RELAPSES = 'INS_RELAPSES'
    MEDICATIONS = 'MEDICATIONS'
    MPGN_CLINICAL_PICTURES = 'MPGN_CLINICAL_PICTURES'
    NEPHRECTOMIES = 'NEPHRECTOMIES'
    NUMBERS = 'NUMBERS'
    PATHOLOGY = 'PATHOLOGY'
    PLASMAPHERESIS = 'PLASMAPHERESIS'
    PREGNANCIES = 'PREGNANCIES'
    PRIMARY_DIAGNOSIS = 'PRIMARY_DIAGNOSIS'
    RENAL_IMAGING = 'RENAL_IMAGING'
    RESULTS = 'RESULTS'
    SALT_WASTING_CLINICAL_FEATURES = 'SALT_WASTING_CLINICAL_FEATURES'
    TRANSPLANTS = 'TRANSPLANTS'
    UNITS = 'UNITS'

    def __str__(self):
        return str(self.value)
