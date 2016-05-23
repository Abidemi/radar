from sqlalchemy import Column, Boolean, Index, Integer, ForeignKey, String, Date
from sqlalchemy.orm import relationship

from radar.database import db
from radar.models.common import MetaModelMixin, uuid_pk_column, patient_id_column, patient_relationship
from radar.models.logs import log_changes


PROCESS_MEASURES = [
    'dipstick_urinalysis',
    'medication_review',
    'uss',
    'senior_review',
    'self_management',
    'physiological_monitoring',
    'ue_admission',
    'ue_repeated',
]


@log_changes
class AkiProcessMeasures(db.Model, MetaModelMixin):
    __tablename__ = 'aki_process_measures'

    id = uuid_pk_column()

    patient_id = patient_id_column()
    patient = patient_relationship('aki_process_measures')

    source_group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    source_group = relationship('Group')
    source_type = Column(String, nullable=False)

    date = Column(Date, nullable=False)


for x in PROCESS_MEASURES:
    setattr(AkiProcessMeasures, x, Column(Boolean))


Index('aki_process_measures_patient_id', AkiProcessMeasures.patient_id)
