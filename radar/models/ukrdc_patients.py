from sqlalchemy import and_, exists, or_, PrimaryKeyConstraint, select
from sqlalchemy.orm import relationship

from radar.database import db
from radar.models.medications import Medication
from radar.models.patients import Patient
from radar.models.results import Result
from radar.models.views import create_view


username = 'ukrdc_importer'


class UKRDCPatient(db.Model):
    """View of patients with data from the UKRDC (e.g. medications or results)."""

    __table__ = create_view(
        'ukrdc_patients',
        select([Patient.id])
        .where(
            or_(
                exists().where(and_(Result.patient_id == Patient.id, Result.created_username == username)),
                exists().where(and_(Medication.patient_id == Patient.id, Medication.created_username == username))
            )
        ),
        PrimaryKeyConstraint('id')
    )

    patient = relationship(
        'Patient',
        primaryjoin='UKRDCPatient.id == Patient.id',
        uselist=False,
        backref='ukrdc_patient',
        foreign_keys='Patient.id'
    )
