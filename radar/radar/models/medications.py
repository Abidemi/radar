from collections import OrderedDict
from sqlalchemy import Column, Date, String, ForeignKey, Numeric, Index
from sqlalchemy import Integer
from sqlalchemy.orm import relationship

from radar.database import db
from radar.models.common import MetaModelMixin, uuid_pk_column, patient_id_column, patient_relationship

MEDICATION_ROUTES = OrderedDict([
    ('ORAL', 'Oral'),
    ('RECTAL', 'Rectal'),
])

MEDICATION_DOSE_UNITS = OrderedDict([
    ('ML', 'ml'),
    ('L', 'l'),
    ('MG', 'mg'),
    ('G', 'g'),
    ('KG', 'kg'),
])

MEDICATION_FREQUENCIES = OrderedDict([
    ('DAILY', 'Daily'),
    ('WEEKLY', 'Weekly'),
    ('MONTHLY', 'Monthly'),
])


class Medication(db.Model, MetaModelMixin):
    __tablename__ = 'medications'

    id = uuid_pk_column()

    patient_id = patient_id_column()
    patient = patient_relationship('medications')

    data_source_id = Column(Integer, ForeignKey('data_sources.id'), nullable=False)
    data_source = relationship('DataSource')

    from_date = Column(Date, nullable=False)
    to_date = Column(Date)
    name = Column(String, nullable=False)
    dose_quantity = Column(Numeric, nullable=False)
    dose_unit = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    route = Column(String, nullable=False)

Index('medications_patient_id_idx', Medication.patient_id)
