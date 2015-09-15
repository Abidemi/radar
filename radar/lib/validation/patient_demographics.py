from radar.lib.models.patient_demographics import GENDERS
from radar.lib.validation.core import Validation, Field, pass_new_obj, ValidationError
from radar.lib.validation.data_sources import DataSourceValidationMixin
from radar.lib.validation.meta import MetaValidationMixin
from radar.lib.validation.patients import PatientValidationMixin
from radar.lib.validation.validators import required, not_empty, optional, not_in_future, max_length, in_, \
    none_if_blank, email_address, normalise_whitespace, upper, after_day_zero


class PatientDemographicsValidation(PatientValidationMixin, DataSourceValidationMixin, MetaValidationMixin, Validation):
    first_name = Field([not_empty(), upper(), normalise_whitespace(), max_length(100)])
    last_name = Field([not_empty(), upper(), normalise_whitespace(), max_length(100)])
    date_of_birth = Field([required(), after_day_zero(), not_in_future()])
    date_of_death = Field([optional(), after_day_zero(), not_in_future()])
    gender = Field([required(), upper(), in_(GENDERS.keys())])
    ethnicity_code = Field([required()])
    home_number = Field([none_if_blank(), optional(), normalise_whitespace(), max_length(30)])
    work_number = Field([none_if_blank(), optional(), normalise_whitespace(), max_length(30)])
    mobile_number = Field([none_if_blank(), optional(), normalise_whitespace(), max_length(30)])
    email_address = Field([none_if_blank(), optional(), email_address()])

    @pass_new_obj
    def validate_date_of_death(self, obj, date_of_death):
        if date_of_death < obj.date_of_birth:
            raise ValidationError('Must be after date of birth.')

        return date_of_death
