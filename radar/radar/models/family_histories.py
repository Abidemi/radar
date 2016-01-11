from collections import OrderedDict

from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import orm

from radar.database import db
from radar.models.common import MetaModelMixin, uuid_pk_column, patient_id_column, patient_relationship


RELATIONSHIPS = OrderedDict([
    (1, 'Mother'),
    (2, 'Father'),
    (3, 'Sister'),
    (4, 'Brother'),
    (5, 'Grandmother - Maternal'),
    (6, 'Grandmother - Paternal'),
    (15, 'Grandfather - Maternal'),
    (16, 'Grandfather - Paternal'),
    (7, 'Aunt - Maternal'),
    (8, 'Aunt - Paternal'),
    (9, 'Uncle - Maternal'),
    (10, 'Uncle - Paternal'),
    (11, 'Cousin - Maternal'),
    (12, 'Cousin - Paternal'),
    (13, 'Half Sister'),
    (14, 'Half Brother'),
])


class FamilyHistory(db.Model, MetaModelMixin):
    __tablename__ = 'family_histories'

    id = uuid_pk_column()

    patient_id = patient_id_column()
    patient = patient_relationship('family_histories')

    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    group = orm.relationship('Group')

    parental_consanguinity = Column(Boolean)
    family_history = Column(Boolean)
    other_family_history = Column(String)

Index('family_histories_patient_id_idx', FamilyHistory.patient_id)
Index('family_histories_group_id_idx', FamilyHistory.group_id)
Index(
    'family_histories_patient_id_group_id_idx',
    FamilyHistory.patient_id,
    FamilyHistory.group_id,
    unique=True
)


class FamilyHistoryRelative(db.Model):
    __tablename__ = 'family_history_relatives'

    id = Column(Integer, primary_key=True)

    family_history_id = Column(UUID, ForeignKey('family_histories.id'), nullable=False)
    family_history = orm.relationship('FamilyHistory', backref=orm.backref('relatives', cascade='all, delete-orphan', passive_deletes=True))

    relationship = Column(Integer, nullable=False)

    # TODO null when patient is deleted
    patient_id = Column(Integer, ForeignKey('patients.id'))
    patient = orm.relationship('Patient')

Index('family_history_relatives_family_history_id_idx', FamilyHistoryRelative.family_history_id)
