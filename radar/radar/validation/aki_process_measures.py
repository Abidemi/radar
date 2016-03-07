from radar.validation.core import Validation, Field
from radar.validation.patients import PatientValidationMixin
from radar.validation.validators import optional
from radar.validation.meta import MetaValidationMixin
from radar.validation.sources import SourceValidationMixin


class AkiProcessMeasuresValidation(PatientValidationMixin, SourceValidationMixin, MetaValidationMixin, Validation):
    dipstick_urinalysis = Field([optional()])
    medication_review = Field([optional()])
    uss = Field([optional()])
    senior_review = Field([optional()])
    self_management = Field([optional()])
    physiological_monitoring = Field([optional()])
    ue_admission = Field([optional()])
    ue_repeated = Field([optional()])
