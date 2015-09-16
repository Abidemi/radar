from radar.lib.validation.core import Validation, Field, ValidationError, pass_new_obj
from radar.lib.validation.data_sources import RadarDataSourceValidationMixin
from radar.lib.validation.meta import MetaValidationMixin
from radar.lib.validation.patients import PatientValidationMixin
from radar.lib.validation.validators import required, after_date_of_birth, max_length, optional, none_if_blank, postcode, \
    not_empty, remove_trailing_comma, normalise_whitespace


class PatientAddressValidation(PatientValidationMixin, RadarDataSourceValidationMixin, MetaValidationMixin, Validation):
    from_date = Field([optional(), after_date_of_birth()])
    to_date = Field([optional(), after_date_of_birth()])
    address_line_1 = Field([
        not_empty(),
        remove_trailing_comma(),
        not_empty(),
        normalise_whitespace(),
        max_length(100)
    ])
    address_line_2 = Field([
        none_if_blank(),
        optional(),
        remove_trailing_comma(),
        none_if_blank(),
        optional(),
        normalise_whitespace(),
        max_length(100)
    ])
    address_line_3 = Field([
        none_if_blank(),
        optional(),
        remove_trailing_comma(),
        none_if_blank(),
        optional(),
        normalise_whitespace(),
        max_length(100)
    ])
    postcode = Field([
        required(),
        postcode()
    ])

    @pass_new_obj
    def validate_to_date(self, obj, to_date):
        if obj.from_date is not None and to_date < obj.from_date:
            raise ValidationError('Must be on or after from date.')

        return to_date