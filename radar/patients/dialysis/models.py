from radar.database import db
from radar.models import DataSource, PatientMixin, CreatedModifiedMixin, UnitMixin, LookupTableMixin
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship


class Dialysis(DataSource, PatientMixin, CreatedModifiedMixin, UnitMixin):
    __tablename__ = 'dialysis'

    id = Column(Integer, ForeignKey('data_sources.id'), primary_key=True)

    date_started = Column(DateTime(timezone=True), nullable=False)
    date_stopped = Column(DateTime(timezone=True))
    dialysis_type_id = Column(Integer, nullable=False)
    dialysis_type = relationship('DialysisType')

    def can_view(self, user):
        return self.patient.can_view(user)

    def can_edit(self, user):
        return self.patient.can_edit(user)

    __mapper_args__ = {
        'polymorphic_identity': 'dialysis',
    }


class DialysisType(db.Model, LookupTableMixin):
    __table_name__ = 'dialysis_types'