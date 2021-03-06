from cornflake.exceptions import ValidationError
import pytest

from radar.api.serializers.validators import nhsbt_no


def test_valid_int():
    value = valid(168292)
    assert value == 168292


def test_valid_string():
    value = valid('168292')
    assert value == '168292'


def test_remove_spaces():
    value = valid('168 292')
    assert value == '168292'


def test_remove_leading_zeros():
    valid('000168292')


def test_invalid():
    invalid('HELLO')


def test_invalid_slash():
    invalid('168/292')


def valid(value):
    return nhsbt_no()(value)


def invalid(value):
    with pytest.raises(ValidationError) as e:
        nhsbt_no()(value)

    return e
