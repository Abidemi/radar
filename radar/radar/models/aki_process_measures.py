from sqlalchemy import Column, Boolean, Index

from radar.database import db
from radar.models.common import MetaModelMixin, uuid_pk_column, patient_id_column, patient_relationship
from radar.models.logs import log_changes


@log_changes
class AkiProcessMeasures(db.Model, MetaModelMixin):
    __tablename__ = 'aki_process_measures'

    id = uuid_pk_column()

    patient_id = patient_id_column()
    patient = patient_relationship('aki_process_measures')

    dipstick_urinalysis = Column(Boolean)
    medication_review = Column(Boolean)
    uss = Column(Boolean)
    senior_review = Column(Boolean)
    self_management = Column(Boolean)
    physiological_monitoring = Column(Boolean)
    ue_admission = Column(Boolean)
    ue_repeated = Column(Boolean)

Index('aki_process_measures_patient_id', AkiProcessMeasures.patient_id)
