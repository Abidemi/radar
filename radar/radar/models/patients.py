from collections import OrderedDict
from datetime import datetime
from sqlalchemy import Column, Integer, select, Boolean, join, String, text

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import aliased
from radar.database import db
from radar.models import MetaModelMixin
from radar.models.patient_demographics import PatientDemographics
from radar.models.cohorts import Cohort, CohortPatient
from radar.cohorts import is_radar_cohort

GENDER_NOT_KNOWN = 0
GENDER_MALE = 1
GENDER_FEMALE = 2
GENDER_NOT_SPECIFIED = 9

GENDERS = OrderedDict([
    (GENDER_NOT_KNOWN, 'Not Known'),
    (GENDER_MALE, 'Male'),
    (GENDER_FEMALE, 'Female'),
    (GENDER_NOT_SPECIFIED, 'Not Specified'),
])

ETHNICITIES = OrderedDict([
    ('A', 'White - British'),
    ('B', 'White - Irish'),
    ('C', 'Other White Background'),
    ('D', 'Mixed - White and Black Caribbean'),
    ('E', 'Mixed - White and Black African'),
    ('F', 'Mixed - White and Asian'),
    ('G', 'Other Mixed Background'),
    ('H', 'Asian or Asian British - Indian'),
    ('J', 'Asian or Asian British - Pakistani'),
    ('K', 'Asian or Asian British - Bangladeshi'),
    ('L', 'Other Asian Background'),
    ('M', 'Black Carribean'),
    ('N', 'Black African'),
    ('P', 'Other Black Background'),
    ('R', 'Chinese'),
    ('S', 'Other Ethnic Background'),
    ('Z', 'Refused / Not Stated'),
])


class Patient(db.Model, MetaModelMixin):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)

    is_active = Column(Boolean, nullable=False, default=True, server_default=text('true'))
    comments = Column(String)

    @property
    def organisations(self):
        return [x.organisation for x in self.organisation_patients]

    @property
    def cohorts(self):
        return [x.cohort for x in self.cohort_patients]

    @hybrid_property
    def recruited_date(self):
        for x in self.cohort_patients:
            if is_radar_cohort(x.cohort):
                return x.recruited_date

        return None

    @recruited_date.expression
    def recruited_date(cls):
        return select([CohortPatient.recruited_date])\
            .select_from(join(CohortPatient, Cohort))\
            .where(CohortPatient.patient_id == cls.id)\
            .where(Cohort.code == 'RADAR')\
            .limit(1)\
            .as_scalar()

    def latest_demographics_attr(self, attr):
        demographics = self.latest_demographics

        if demographics is None:
            return None

        return getattr(demographics, attr)

    @classmethod
    def latest_demographics_query(cls, column):
        patient_alias = aliased(Patient)

        return select([column])\
            .select_from(join(PatientDemographics, patient_alias))\
            .where(patient_alias.id == cls.id)\
            .order_by(PatientDemographics.modified_date.desc())\
            .limit(1)\
            .as_scalar()

    @property
    def latest_demographics(self):
        patient_demographics = self.patient_demographics

        if len(patient_demographics) == 0:
            return None

        def by_modified_date(x):
            return x.modified_date or datetime.min

        return max(patient_demographics, key=by_modified_date)

    @hybrid_property
    def first_name(self):
        return self.latest_demographics_attr('first_name')

    @hybrid_property
    def last_name(self):
        return self.latest_demographics_attr('last_name')

    @hybrid_property
    def date_of_birth(self):
        return self.latest_demographics_attr('date_of_birth')

    @hybrid_property
    def date_of_death(self):
        return self.latest_demographics_attr('date_of_death')

    @hybrid_property
    def ethnicity(self):
        return self.latest_demographics_attr('ethnicity')

    @hybrid_property
    def gender(self):
        return self.latest_demographics_attr('gender')

    @hybrid_property
    def is_male(self):
        return self.gender == GENDER_MALE

    @hybrid_property
    def is_female(self):
        return self.gender == GENDER_FEMALE

    @first_name.expression
    def first_name(cls):
        return cls.latest_demographics_query(PatientDemographics.first_name)

    @last_name.expression
    def last_name(cls):
        return cls.latest_demographics_query(PatientDemographics.last_name)

    @date_of_birth.expression
    def date_of_birth(cls):
        return cls.latest_demographics_query(PatientDemographics.date_of_birth)

    @date_of_death.expression
    def date_of_death(cls):
        return cls.latest_demographics_query(PatientDemographics.date_of_death)

    @ethnicity.expression
    def ethnicity(cls):
        return cls.latest_demographics_query(PatientDemographics.ethnicity)

    @gender.expression
    def gender(cls):
        return cls.latest_demographics_query(PatientDemographics.gender)

    @property
    def earliest_date_of_birth(self):
        earliest_date_of_birth = None

        for demographics in self.patient_demographics:
            date_of_birth = demographics.date_of_birth

            if date_of_birth is not None and (earliest_date_of_birth is None or date_of_birth < earliest_date_of_birth):
                earliest_date_of_birth = date_of_birth

        return earliest_date_of_birth

    def in_cohort(self, cohort):
        print self.cohort_patients
        return any(x == cohort for x in self.cohorts)

    def in_organisation(self, organisation):
        return any(x == organisation for x in self.organisations)
