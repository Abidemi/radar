from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, orm

from radar.database import db
from radar.models.common import MetaModelMixin, patient_id_column, patient_relationship, uuid_pk_column
from radar.models.logs import log_changes


@log_changes
class Consent(db.Model, MetaModelMixin):
    __tablename__ = 'consents'

    id = uuid_pk_column()

    patient_id = patient_id_column()
    patient = patient_relationship('consents')

    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    group = orm.relationship('Group')

    consented_on = Column(Date, nullable=False)
    consent_withdrawn = Column(Date)
    reconsent = Column(Boolean)
