from datetime import date, timedelta

import pytest

from radar.models import Patient, PatientDemographics, Transplant
from radar.models.groups import Group
from radar.models.source_types import SourceType, SOURCE_TYPE_RADAR
from radar.validation.core import ValidationError
from radar.validation.transplants import TransplantValidation
from radar.tests.validation.helpers import validation_runner


@pytest.fixture
def patient():
    patient = Patient()
    patient_demographics = PatientDemographics()
    patient_demographics.date_of_birth = date(2000, 1, 1)
    patient.patient_demographics.append(patient_demographics)
    return patient


@pytest.fixture
def transplant(patient):
    obj = Transplant()
    obj.source_group = Group()
    obj.source_type = SourceType(id=SOURCE_TYPE_RADAR)
    obj.patient = patient
    obj.date = date(2015, 1, 1)
    obj.modality = 29
    obj.date_of_failure = date(2015, 1, 2)
    return obj


def test_valid(transplant):
    obj = valid(transplant)
    assert obj.date == date(2015, 1, 1)
    assert obj.modality == 29
    assert obj.date_of_failure == date(2015, 1, 2)
    assert obj.created_date is not None
    assert obj.modified_date is not None
    assert obj.created_user is not None
    assert obj.modified_user is not None


def test_patient_missing(transplant):
    transplant.patient = None
    invalid(transplant)


def test_source_group_missing(transplant):
    transplant.source_group = None
    invalid(transplant)


def test_source_type_missing(transplant):
    transplant.source_type = None
    transplant = valid(transplant)
    assert transplant.source_type.id == 'RADAR'


def test_date_missing(transplant):
    transplant.date = None
    invalid(transplant)


def test_date_before_dob(transplant):
    transplant.date = date(1999, 1, 1)
    invalid(transplant)


def test_date_future(transplant):
    transplant.date = date.today() + timedelta(days=1)
    invalid(transplant)


def test_modality_missing(transplant):
    transplant.modality = None
    invalid(transplant)


def test_modality_invalid(transplant):
    transplant.modality = 0
    invalid(transplant)


def test_date_of_failure_missing(transplant):
    transplant.date_of_failure = None
    valid(transplant)


def test_date_of_failure_before_dob(transplant):
    transplant.date_of_failure = date(1999, 1, 1)
    invalid(transplant)


def test_date_of_failure_future(transplant):
    transplant.date_of_failure = date.today() + timedelta(days=1)
    invalid(transplant)


def test_date_of_failure_before_transplant_date(transplant):
    transplant.date_of_failure = transplant.date - timedelta(days=1)
    invalid(transplant)


def invalid(obj, **kwargs):
    with pytest.raises(ValidationError) as e:
        valid(obj, **kwargs)

    return e


def valid(obj, **kwargs):
    return validation_runner(Transplant, TransplantValidation, obj, **kwargs)
