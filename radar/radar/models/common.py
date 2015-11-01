from sqlalchemy import Integer, Column, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

from radar.database import db


class UUIDPKColumn(Column):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('primary_key', True)
        kwargs.setdefault('server_default', text('uuid_generate_v4()'))
        super(UUIDPKColumn, self).__init__(UUID, *args, **kwargs)


class CreatedUserMixin(object):
    @declared_attr
    def created_user_id(cls):
        return Column(Integer, ForeignKey('users.id'), nullable=False)

    @declared_attr
    def created_user(cls):
        return relationship('User', primaryjoin="User.id == %s.created_user_id" % cls.__name__)


class CreatedDateMixin(object):
    @declared_attr
    def created_date(cls):
        return Column(DateTime(timezone=True), nullable=False)


class ModifiedUserMixin(object):
    @declared_attr
    def modified_user_id(cls):
        return Column(Integer, ForeignKey('users.id'), nullable=False)

    @declared_attr
    def modified_user(cls):
        return relationship('User', primaryjoin="User.id == %s.modified_user_id" % cls.__name__)


class ModifiedDateMixin(object):
    @declared_attr
    def modified_date(cls):
        return Column(DateTime(timezone=True), nullable=False)


class CreatedMixin(CreatedUserMixin, CreatedDateMixin):
    pass


class ModifiedMixin(ModifiedUserMixin, ModifiedDateMixin):
    pass


class MetaModelMixin(CreatedMixin, ModifiedMixin):
    pass


class IntegerLookupTable(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)


class StringLookupTable(db.Model):
    __abstract__ = True

    id = Column(String, primary_key=True)
    label = Column(String, nullable=False)
