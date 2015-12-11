from enum import Enum


class FEATURES(Enum):
    ADDRESSES = 'ADDRESSES'
    ALIASES = 'ALIASES'
    COHORTS = 'COHORTS'
    COMORBIDITIES = 'COMORBIDITIES'
    DEMOGRAPHICS = 'DEMOGRAPHICS'
    DIAGNOSES = 'DIAGNOSES'
    DIALYSIS = 'DIALYSIS'
    FAMILY_HISTORY = 'FAMILY_HISTORY'
    FETAL_ANOMALY_SCANS = 'FETAL_ANOMALY_SCANS'
    GENETICS = 'GENETICS'
    HOSPITALISATIONS = 'HOSPITALISATIONS'
    INS_CLINICAL_PICTURES = 'INS_CLINICAL_PICTURES'
    INS_RELAPSES = 'INS_RELAPSES'
    MEDICATIONS = 'MEDICATIONS'
    NEPHRECTOMIES = 'NEPHRECTOMIES'
    NUMBERS = 'NUMBERS'
    PATHOLOGY = 'PATHOLOGY'
    PLASMAPHERESIS = 'PLASMAPHERESIS'
    RENAL_IMAGING = 'RENAL_IMAGING'
    RESULTS = 'RESULTS'
    SALT_WASTING_CLINICAL_FEATURES = 'SALT_WASTING_CLINICAL_FEATURES'
    TRANSPLANTS = 'TRANSPLANTS'
    UNITS = 'UNITS'

    def __str__(self):
        return str(self.value)
