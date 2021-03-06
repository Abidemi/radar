from cornflake.exceptions import ValidationError
import pytest

from radar.api.serializers.validators import hsc_no


def test_valid_int():
    assert valid(3232255825) == 3232255825
    assert valid(3232255825) == 3232255825


def test_valid_string():
    assert valid('3232255825') == '3232255825'
    assert valid('3232255825') == '3232255825'


def test_nhs_no():
    invalid('9434765919')


def test_chi_no():
    invalid('101299877')


def valid(value):
    return hsc_no()(value)


def invalid(value):
    with pytest.raises(ValidationError) as e:
        hsc_no()(value)

    return e
