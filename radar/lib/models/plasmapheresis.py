from collections import OrderedDict
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy import Date
from sqlalchemy.orm import relationship

from radar.lib.database import db
from radar.lib.models.common import MetaModelMixin

PLASMAPHERESIS_RESPONSES = OrderedDict([
    ('COMPLETE', 'Complete'),
    ('PARTIAL', 'Partial'),
    ('NONE', 'None'),
])

PLASMAPHERESIS_NO_OF_EXCHANGES = OrderedDict([
    ('1/1D', 'Daily'),
    ('5/1W', 'x5 / week'),
    ('4/1W', 'x4 / week'),
    ('3/1W', 'x3 / week'),
    ('2/1W', 'x2 / week'),
    ('1/1W', 'x1 / week'),
    ('1/2W', 'x1 / 2 weeks'),
    ('1/4W', 'x1 / 4 weeks'),
])


class Plasmapheresis(db.Model, MetaModelMixin):
    __tablename__ = 'plasmapheresis'

    id = Column(Integer, primary_key=True)

    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    patient = relationship('Patient')

    data_source_id = Column(Integer, ForeignKey('data_sources.id'), nullable=False)
    data_source = relationship('DataSource')

    from_date = Column(Date, nullable=False)
    to_date = Column(Date)
    no_of_exchanges = Column(String)
    response = Column(String)
