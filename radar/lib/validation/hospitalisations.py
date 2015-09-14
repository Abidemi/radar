from radar.lib.validation.core import Validation, Field, pass_new_obj, ValidationError
from radar.lib.validation.data_sources import DataSourceValidationMixin
from radar.lib.validation.patients import PatientValidationMixin
from radar.lib.validation.validators import required, optional, valid_date_for_patient, max_length, none_if_blank


class HospitalisationValidation(PatientValidationMixin, DataSourceValidationMixin, Validation):
    date_of_admission = Field(chain=[required(), valid_date_for_patient()])
    date_of_discharge = Field(chain=[optional(), valid_date_for_patient()])
    reason_for_admission = Field(chain=[none_if_blank(), optional(), max_length(1000)])
    comments = Field(chain=[none_if_blank(), optional(), max_length(10000)])

    @pass_new_obj
    def validate_date_of_discharge(self, obj, date_of_discharge):
        if date_of_discharge < obj.date_of_admission:
            raise ValidationError('Must be on or before date of admission.')

        return date_of_discharge
