from radar.permissions import can_view_demographics
from radar.roles import COHORT_ROLES, ORGANISATION_ROLES
from radar.tests.permissions.helpers import make_cohorts, make_user, make_patient, make_organisations


def test_admin():
    patient = make_patient()
    user = make_user()

    assert not can_view_demographics(user, patient)

    user.is_admin = True

    assert can_view_demographics(user, patient)


def test_intersecting_cohorts_with_view_demographics_permission():
    cohorts = make_cohorts(3)
    cohort_a, cohort_b, cohort_c = cohorts
    patient = make_patient(cohorts=cohorts)
    user = make_user(cohorts=[cohort_a, [cohort_b, COHORT_ROLES.SENIOR_RESEARCHER], cohort_c])

    assert can_view_demographics(user, patient)


def test_intersecting_cohorts_without_view_demographics_permission():
    cohort_a, cohort_b = make_cohorts(2)

    patient = make_patient(cohorts=[cohort_a])
    user = make_user(cohorts=[[cohort_b, COHORT_ROLES.RESEARCHER]])

    assert not can_view_demographics(user, patient)


def test_disjoint_cohorts_with_view_demographics_permission():
    cohort_a, cohort_b = make_cohorts(2)

    patient = make_patient(cohorts=[cohort_a])
    user = make_user(cohorts=[[cohort_b, COHORT_ROLES.SENIOR_RESEARCHER]])

    assert not can_view_demographics(user, patient)


def test_intersecting_organisations_with_view_demographics_permission():
    organisations = make_organisations(3)
    organisation_a, organisation_b, organisation_c = organisations
    patient = make_patient(organisations=organisations)
    user = make_user(organisations=[organisation_a, [organisation_b, ORGANISATION_ROLES.CLINICIAN], organisation_c])

    assert can_view_demographics(user, patient)


def test_intersecting_organisations_without_view_demographics_permission():
    organisations = make_organisations(3)
    patient = make_patient(organisations=organisations)
    user = make_user(organisations=organisations)

    assert not can_view_demographics(user, patient)


def test_disjoint_organisations_with_view_demographics_permission():
    organisation_a, organisation_b = make_organisations(2)

    patient = make_patient(organisations=[organisation_a])
    user = make_user(cohorts=[[organisation_b, ORGANISATION_ROLES.CLINICIAN]])

    assert not can_view_demographics(user, patient)
