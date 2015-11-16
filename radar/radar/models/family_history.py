from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, Index
from sqlalchemy.orm import relationship

from radar.database import db
from radar.models.common import MetaModelMixin, uuid_pk_column, patient_id_column, patient_relationship


class FamilyHistory(db.Model, MetaModelMixin):
    __tablename__ = 'family_history'

    id = uuid_pk_column()

    patient_id = patient_id_column()
    patient = patient_relationship('family_history')

    cohort_id = Column(Integer, ForeignKey('cohorts.id'), nullable=False)
    cohort = relationship('Cohort')

    parental_consanguinity = Column(Boolean, nullable=False)
    family_history = Column(Boolean, nullable=False)
    other_family_history = Column(String)

Index('family_history_patient_id_idx', FamilyHistory.patient_id)
Index('family_history_cohort_id_idx', FamilyHistory.cohort_id)
