from datetime import date

import pytest

from radar.models import Patient, PatientDemographics, DataSource, PatientAlias
from radar.validation.core import ValidationError
from radar.validation.patient_aliases import PatientAliasValidation
from helpers.validation import validation_runner


@pytest.fixture
def patient():
    patient = Patient()
    patient_demographics = PatientDemographics()
    patient_demographics.date_of_birth = date(2000, 1, 1)
    patient.patient_demographics.append(patient_demographics)
    return patient


@pytest.fixture
def alias(patient):
    obj = PatientAlias()
    obj.data_source = DataSource()
    obj.patient = patient
    obj.first_name = 'JOHN'
    obj.last_name = 'SMITH'
    return obj


def test_valid(alias):
    obj = valid(alias)
    assert obj.first_name == 'JOHN'
    assert obj.last_name == 'SMITH'
    assert obj.created_date is not None
    assert obj.modified_date is not None
    assert obj.created_user is not None
    assert obj.modified_user is not None


def test_patient_missing(alias):
    alias.patient = None
    invalid(alias)


def test_data_source_missing(alias):
    alias.data_source = None
    invalid(alias)


def test_first_name_blank(alias):
    alias.first_name = ''
    invalid(alias)


def test_first_name_missing(alias):
    alias.first_name = None
    invalid(alias)


def test_first_name_whitespace(alias):
    alias.first_name = 'FOO  BAR'
    obj = valid(alias)
    assert obj.first_name == 'FOO BAR'


def test_first_name_to_upper(alias):
    alias.first_name = 'foo bar'
    obj = valid(alias)
    assert obj.first_name == 'FOO BAR'


def test_last_name_blank(alias):
    alias.last_name = ''
    invalid(alias)


def test_last_name_missing(alias):
    alias.last_name = None
    invalid(alias)


def test_last_name_whitespace(alias):
    alias.last_name = 'FOO  BAR'
    obj = valid(alias)
    assert obj.last_name == 'FOO BAR'


def test_last_name_to_upper(alias):
    alias.last_name = 'foo bar'
    obj = valid(alias)
    assert obj.last_name == 'FOO BAR'


def invalid(obj, **kwargs):
    with pytest.raises(ValidationError) as e:
        valid(obj, **kwargs)

    return e


def valid(obj, **kwargs):
    return validation_runner(PatientAlias, PatientAliasValidation, obj, **kwargs)
