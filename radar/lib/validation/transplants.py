from radar.lib.validation.core import run_validators
from radar.lib.validation.validators import required, not_in_future


def validate_transplant(errors, obj):
    run_validators(errors, 'transplant_date', obj.transplant_date, [required, not_in_future])
    run_validators(errors, 'transplant_type', obj.transplant_type, [required])
