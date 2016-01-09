from radar.validation.core import Validation, Field
from radar.validation.data_sources import DataSourceValidationMixin
from radar.validation.meta import MetaValidationMixin
from radar.validation.patients import PatientValidationMixin
from radar.validation.validators import required, valid_date_for_patient


class ResultValidation(PatientValidationMixin, DataSourceValidationMixin, MetaValidationMixin, Validation):
    observation = Field([required()])
    date = Field([required(), valid_date_for_patient()])
    value = Field([required()])
