from sqlalchemy import Column, Integer, ForeignKey, String, Index, CheckConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects import postgresql

from radar.database import db
from radar.models.common import uuid_pk_column, MetaModelMixin, patient_id_column, patient_relationship
from radar.models.logs import log_changes


class Form(db.Model):
    __tablename__ = 'forms'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, CheckConstraint("slug similar to '([a-z0-9]+-)*[a-z0-9]+'"), nullable=False, unique=True)
    data = Column(postgresql.JSONB, nullable=False)


@log_changes
class Entry(db.Model, MetaModelMixin):
    __tablename__ = 'entries'

    id = uuid_pk_column()

    patient_id = patient_id_column()
    patient = patient_relationship('entries')

    form_id = Column(Integer, ForeignKey('forms.id'), nullable=False)
    form = relationship('Form')

    data = Column(postgresql.JSONB, nullable=False)

Index('entries_patient_idx', Entry.patient_id)


class GroupForm(db.Model):
    __tablename__ = 'group_forms'

    id = Column(Integer, primary_key=True)

    group_id = Column(Integer, ForeignKey('groups.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    group = relationship('Group', backref=backref('group_forms', cascade='all, delete-orphan', passive_deletes=True))

    form_id = Column(Integer, ForeignKey('forms.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    form = relationship('Form', backref=backref('group_forms', cascade='all, delete-orphan', passive_deletes=True))

    weight = Column(Integer, CheckConstraint('weight >= 0'), nullable=False)

Index('group_forms_group_idx', GroupForm.group_id)
Index('group_forms_form_idx', GroupForm.form_id)
Index('group_forms_form_group_idx', GroupForm.form_id, GroupForm.group_id, unique=True)


class GroupQuestionnaire(db.Model):
    __tablename__ = 'group_questionnaires'

    id = Column(Integer, primary_key=True)

    group_id = Column(Integer, ForeignKey('groups.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    group = relationship('Group', backref=backref('group_questionnaires', cascade='all, delete-orphan', passive_deletes=True))

    form_id = Column(Integer, ForeignKey('forms.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    form = relationship('Form', backref=backref('group_questionnaires', cascade='all, delete-orphan', passive_deletes=True))

    weight = Column(Integer, CheckConstraint('weight >= 0'), nullable=False)

Index('group_questionnaires_group_idx', GroupQuestionnaire.group_id)
Index('group_questionnaires_form_idx', GroupQuestionnaire.form_id)
Index('group_questionnaires_form_group_idx', GroupQuestionnaire.form_id, GroupQuestionnaire.group_id, unique=True)
