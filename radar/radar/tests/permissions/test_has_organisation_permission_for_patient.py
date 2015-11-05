from radar.permissions import has_organisation_permission_for_patient, \
    has_group_permission_for_patient
from radar.tests.permissions.helpers import make_user, make_patient, make_organisations
from radar.models.organisations import Organisation
from radar.roles import ORGANISATION_IT, ORGANISATION_CLINICIAN

VIEW_PATIENT = 'has_view_patient_permission'


def should_grant(user, patient, permission):
    assert has_organisation_permission_for_patient(user, patient, permission)


def should_deny(user, patient, permission):
    assert not has_organisation_permission_for_patient(user, patient, permission)
    assert not has_group_permission_for_patient(user, patient, permission)


def test_admin():
    user = make_user()
    patient = make_patient()

    should_deny(user, patient, VIEW_PATIENT)

    user.is_admin = True

    should_grant(user, patient, VIEW_PATIENT)


def test_intersecting_organisations():
    organisation = Organisation()
    patient = make_patient(organisations=[organisation])
    user_a = make_user(organisations=[(organisation, ORGANISATION_IT)])
    user_b = make_user(organisations=[(organisation, ORGANISATION_CLINICIAN)])

    should_deny(user_a, patient, VIEW_PATIENT)
    should_grant(user_b, patient, VIEW_PATIENT)


def test_disjoint_organisations():
    organisation_a, organisation_b = make_organisations(2)
    patient = make_patient(organisations=[organisation_a])
    user_a = make_user(organisations=[(organisation_b, ORGANISATION_IT)])
    user_b = make_user(organisations=[(organisation_b, ORGANISATION_CLINICIAN)])

    should_deny(user_a, patient, VIEW_PATIENT)
    should_deny(user_b, patient, VIEW_PATIENT)
