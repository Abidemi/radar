from flask import url_for
from sqlalchemy import Column, Date, String, ForeignKey, Numeric
from sqlalchemy import Integer
from sqlalchemy.orm import relationship

from radar.lib.database import db
from radar.lib.concept_maps.medications import MedicationConceptMap
from radar.models.common import DataSource, PatientMixin, MetadataMixin, StringLookupTableMixin, UnitMixin


class Medication(DataSource, PatientMixin, MetadataMixin, UnitMixin):
    __tablename__ = 'medications'

    id = Column(Integer, ForeignKey('data_sources.id'), primary_key=True)

    from_date = Column(Date, nullable=False)
    to_date = Column(Date)

    name = Column(String, nullable=False)

    dose_quantity = Column(Numeric, nullable=False)

    dose_unit_id = Column(String, ForeignKey('medication_dose_units.id'), nullable=False)
    dose_unit = relationship('MedicationDoseUnit')

    frequency_id = Column(String, ForeignKey('medication_frequencies.id'), nullable=False)
    frequency = relationship('MedicationFrequency')

    route_id = Column(String, ForeignKey('medication_routes.id'), nullable=False)
    route = relationship('MedicationRoute')

    __mapper_args__ = {
        'polymorphic_identity': 'medications',
    }

    def can_view(self, user):
        return self.patient.can_view(user)

    def can_edit(self, user):
        return self.patient.can_edit(user)

    def concept_map(self):
        return MedicationConceptMap(self)

    def view_url(self):
        return url_for('medications.view_medication', patient_id=self.patient.id, medication_id=self.id)

    def edit_url(self):
        return url_for('medications.edit_medication', patient_id=self.patient.id, medication_id=self.id)

    def delete_url(self):
        return url_for('medications.delete_medication', patient_id=self.patient.id, medication_id=self.id)


class MedicationFrequency(db.Model, StringLookupTableMixin):
    __tablename__ = 'medication_frequencies'


class MedicationRoute(db.Model, StringLookupTableMixin):
    __tablename__ = 'medication_routes'


class MedicationDoseUnit(db.Model, StringLookupTableMixin):
    __tablename__ = 'medication_dose_units'