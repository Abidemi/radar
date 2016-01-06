from collections import OrderedDict

from sqlalchemy import Column, Date, Integer

from radar.database import db
from radar.models.common import MetaModelMixin, uuid_pk_column, patient_id_column, patient_relationship

DEAFNESS_NO = 1
DEAFNESS_MINOR = 2
DEAFNESS_HEARING_AID = 3

DEAFNESS_OPTIONS = OrderedDict([
    (DEAFNESS_NO, 'No'),
    (DEAFNESS_MINOR, 'Yes - Minor'),
    (DEAFNESS_HEARING_AID, 'Yes - Hearing Aid Needed'),
])


class AlportClinicalPicture(db.Model, MetaModelMixin):
    __tablename__ = 'alport_clinical_pictures'

    id = uuid_pk_column()

    patient_id = patient_id_column()
    patient = patient_relationship('alport_clinical_pictures')

    date_of_picture = Column(Date, nullable=False)
    deafness = Column(Integer, nullable=False)
    deafness_date = Column(Date)
    hearing_aid_date = Column(Date)
