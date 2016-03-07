from radar.validation.core import Validation, Field
from radar.validation.patients import PatientValidationMixin
from radar.validation.validators import optional, required
from radar.validation.meta import MetaValidationMixin
from radar.validation.sources import SourceValidationMixin
from radar.models.aki_process_measures import PROCESS_MEASURES


class AkiProcessMeasuresValidation(PatientValidationMixin, SourceValidationMixin, MetaValidationMixin, Validation):
    date = Field([required()])

for x in PROCESS_MEASURES:
    setattr(AkiProcessMeasuresValidation, x, Field([optional()]))
