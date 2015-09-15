from sqlalchemy import Column, Integer, ForeignKey, String, Date
from sqlalchemy.orm import relationship
from radar.lib.database import db
from radar.lib.models import MetaModelMixin, IntegerLookupTable


class Comorbidity(db.Model, MetaModelMixin):
    __tablename__ = 'comorbidities'

    id = Column(Integer, primary_key=True)

    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    patient = relationship('Patient')

    data_source_id = Column(Integer, ForeignKey('data_sources.id'), nullable=False)
    data_source = relationship('DataSource')

    from_date = Column(Date, nullable=False)
    to_date = Column(Date)

    disorder_id = Column(Integer, ForeignKey('disorders.id'), nullable=False)
    disorder = relationship('Disorder')


class Disorder(IntegerLookupTable):
    __tablename__ = 'disorders'
