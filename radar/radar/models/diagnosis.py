from collections import OrderedDict

from sqlalchemy import Column, Integer, ForeignKey, Date, String, Index
from sqlalchemy.orm import relationship

from radar.database import db
from radar.models.common import MetaModelMixin, uuid_pk_column, patient_id_column, patient_relationship
from radar.utils import to_age

DIAGNOSIS_BIOPSY_DIAGNOSES = OrderedDict([
    (1, 'Minimal Change'),
    (2, 'FSGS'),
    (3, 'Mesangial Hyperthrophy'),
    (4, 'Other'),
    (5, 'No BX @ Time of Diagnosis'),
])


class Diagnosis(db.Model, MetaModelMixin):
    __tablename__ = 'diagnoses'

    id = uuid_pk_column()

    patient_id = patient_id_column()
    patient = patient_relationship('diagnoses')

    cohort_id = Column(Integer, ForeignKey('cohorts.id'), nullable=False)
    cohort = relationship('Cohort')

    date_of_onset = Column(Date, nullable=False)
    date_of_diagnosis = Column(Date, nullable=False)

    cohort_diagnosis_id = Column(Integer, ForeignKey('cohort_diagnoses.id'), nullable=False)
    cohort_diagnosis = relationship('CohortDiagnosis')

    diagnosis_text = Column(String)
    biopsy_diagnosis = Column(Integer)

    @property
    def age_at_onset(self):
        x = to_age(self.patient, self.date_of_onset)
        return x

    @property
    def age_at_diagnosis(self):
        return to_age(self.patient, self.date_of_diagnosis)

Index('diagnoses_patient_id_idx', Diagnosis.patient_id)
Index('diagnoses_cohort_id_idx', Diagnosis.cohort_id)


class CohortDiagnosis(db.Model):
    __tablename__ = 'cohort_diagnoses'

    id = Column(Integer, primary_key=True)

    cohort_id = Column(Integer, ForeignKey('cohorts.id'), nullable=False)
    cohort = relationship('Cohort')

    label = Column(String, nullable=False)

    edta_code = Column(Integer)
    snomed_code = Column(Integer)

Index('cohort_diagnoses_cohort_id_idx', CohortDiagnosis.cohort_id)
