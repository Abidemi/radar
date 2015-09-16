from radar.lib.models import ORGANISATION_CODE_NHS, ORGANISATION_CODE_CHI, ORGANISATION_CODE_HANDC, \
    ORGANISATION_CODE_UKRR, ORGANISATION_CODE_UKRDC, ORGANISATION_CODE_BAPN, ORGANISATION_TYPE_OTHER
from radar.lib.organisations import is_chi_organisation, is_nhs_organisation, is_ukrr_organisation, \
    is_handc_organisation, is_radar_organisation
from radar.lib.validation.core import Validation, pass_call, ValidationError, Field
from radar.lib.validation.data_sources import RadarDataSourceValidationMixin
from radar.lib.validation.meta import MetaValidationMixin
from radar.lib.validation.patients import PatientValidationMixin
from radar.lib.validation.validators import required, max_length, not_empty, normalise_whitespace
from radar.lib.validation.patient_number_validators import nhs_no, chi_no, ukrr_no, handc_no, bapn_no, ukrdc_no


NUMBER_VALIDATORS = {
    ORGANISATION_CODE_NHS: [nhs_no()],
    ORGANISATION_CODE_CHI: [chi_no()],
    ORGANISATION_CODE_HANDC: [handc_no()],
    ORGANISATION_CODE_UKRR: [ukrr_no()],
    ORGANISATION_CODE_UKRDC: [ukrdc_no()],
    ORGANISATION_CODE_BAPN: [bapn_no()]
}


class PatientNumberValidation(PatientValidationMixin, RadarDataSourceValidationMixin, MetaValidationMixin, Validation):
    organisation = Field([required()])
    number = Field([not_empty(), normalise_whitespace(), max_length(50)])

    def validate_organisation(self, organisation):
        if is_radar_organisation(organisation):
            raise ValidationError("Can't add RaDaR numbers.")

        return organisation

    @pass_call
    def validate(self, call, obj):
        organisation = obj.organisation

        if organisation.type == ORGANISATION_TYPE_OTHER:
            number_validators = NUMBER_VALIDATORS.get(organisation.code)

            if number_validators is not None:
                call.validators_for_field(number_validators, obj, self.number)

        return obj
