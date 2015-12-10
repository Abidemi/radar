from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint, Index
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from radar.database import db
from radar.roles import COHORT_PERMISSIONS, COHORT_MANAGED_ROLES, PERMISSIONS, COHORT_ROLES
from radar.models.common import MetaModelMixin, patient_id_column, patient_relationship


class Cohort(db.Model):
    __tablename__ = 'cohorts'

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    short_name = Column(String, nullable=False)
    notes = Column(String)

    cohort_patients = relationship('CohortPatient')
    cohort_users = relationship('CohortUser')
    cohort_features = relationship('CohortFeature')
    cohort_result_group_specs = relationship('CohortResultGroupSpec')

    @property
    def patients(self):
        return [x.patient for x in self.cohort_patients]

    @property
    def users(self):
        return [x.user for x in self.cohort_users]

    @property
    def sorted_result_groups(self):
        return [x.result_group_spec for x in sorted(self.cohort_result_group_specs, key=lambda y: y.weight)]

    @property
    def sorted_features(self):
        return [x.name for x in sorted(self.cohort_features, key=lambda y: y.weight)]


class CohortFeature(db.Model):
    __tablename__ = 'cohort_features'

    id = Column(Integer, primary_key=True)

    cohort_id = Column(Integer, ForeignKey('cohorts.id'))
    cohort = relationship('Cohort')

    name = Column(String, nullable=False)
    weight = Column(Integer, nullable=False)

Index('cohort_features_cohort_id_idx', CohortFeature.cohort_id)


class CohortPatient(db.Model, MetaModelMixin):
    __tablename__ = 'cohort_patients'

    id = Column(Integer, primary_key=True)

    cohort_id = Column(Integer, ForeignKey('cohorts.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    cohort = relationship('Cohort')

    patient_id = patient_id_column()
    patient = patient_relationship('cohort_patients')

    recruited_by_organisation_id = Column(Integer, ForeignKey('organisations.id'), nullable=False)
    recruited_by_organisation = relationship('Organisation')

    is_active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint('cohort_id', 'patient_id'),
    )

    @hybrid_property
    def recruited_date(self):
        return self.created_date

    @recruited_date.setter
    def recruited_date(self, value):
        self.created_date = value

Index('cohort_patients_cohort_id_idx', CohortPatient.cohort_id)
Index('cohort_patients_patient_id_idx', CohortPatient.patient_id)


class CohortUser(db.Model, MetaModelMixin):
    __tablename__ = 'cohort_users'

    id = Column(Integer, primary_key=True)

    cohort_id = Column(Integer, ForeignKey('cohorts.id'), nullable=False)
    cohort = relationship('Cohort')

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', foreign_keys=[user_id])

    _role = Column('role', String, nullable=False)

    __table_args__ = (
        UniqueConstraint('cohort_id', 'user_id'),
    )

    @property
    def role(self):
        value = self._role

        if value is not None:
            value = COHORT_ROLES(value)

        return value

    @role.setter
    def role(self, value):
        if value is not None:
            value = value.value

        self._role = value

    def has_permission(self, permission):
        permission_method = permission.value.lower()
        grant = getattr(self, 'has_' + permission_method + '_permission', None)

        if grant is None:
            roles = COHORT_PERMISSIONS.get(permission, [])
            grant = self.role in roles

        return grant

    @property
    def permissions(self):
        return [x for x in PERMISSIONS if self.has_permission(x)]

    @property
    def has_edit_user_membership_permission(self):
        return len(self.managed_roles) > 0

    @property
    def managed_roles(self):
        return COHORT_MANAGED_ROLES.get(self.role, [])

Index('cohort_users_cohort_id_idx', CohortUser.cohort_id)
Index('cohort_users_user_id_idx', CohortUser.user_id)


class CohortResultGroupSpec(db.Model):
    __tablename__ = 'cohort_result_group_specs'

    id = Column(Integer, primary_key=True)

    cohort_id = Column(Integer, ForeignKey('cohorts.id'), nullable=False)
    cohort = relationship('Cohort')

    result_group_spec_id = Column(Integer, ForeignKey('result_group_specs.id'), nullable=False)
    result_group_spec = relationship('ResultGroupSpec')

    weight = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('cohort_id', 'result_group_spec_id'),
    )

Index('cohort_result_group_specs_cohort_id_idx', CohortResultGroupSpec.cohort_id)
