from collections import OrderedDict

from sqlalchemy import Column, Integer, ForeignKey, Date, Index, String
from sqlalchemy.orm import relationship

from radar.database import db
from radar.models.common import MetaModelMixin, uuid_pk_column

NEPHRECTOMY_KIDNEY_SIDES = OrderedDict([
    ('LEFT', 'Left'),
    ('RIGHT', 'Right'),
    ('BILATERAL', 'Bilateral'),
])

NEPHRECTOMY_KIDNEY_TYPES = OrderedDict([
    ('TRANSPLANT', 'Transplant'),
    ('NATURAL', 'Natural'),
])

NEPHRECTOMY_ENTRY_TYPES = OrderedDict([
    ('O', 'Open'),
    ('HA', 'Hand Assisted'),
    ('TPL', 'Transperitoneal Laparoscopic'),
    ('RPL', 'Retroperitoneal Laparoscopic'),
])


class Nephrectomy(db.Model, MetaModelMixin):
    __tablename__ = 'nephrectomies'

    id = uuid_pk_column()

    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    patient = relationship('Patient')

    data_source_id = Column(Integer, ForeignKey('data_sources.id'), nullable=False)
    data_source = relationship('DataSource')

    date = Column(Date, nullable=False)
    kidney_side = Column(String, nullable=False)
    kidney_type = Column(String, nullable=False)
    entry_type = Column(String, nullable=False)

Index('nephrectomies_patient_id_idx', Nephrectomy.patient_id)
