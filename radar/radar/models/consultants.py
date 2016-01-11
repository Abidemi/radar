from sqlalchemy import Integer, Column, String

from radar.database import db
from radar.models.common import MetaModelMixin


class Consultant(db.Model, MetaModelMixin):
    __tablename__ = 'consultants'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String)
    telephone_number = Column(String)
    gmc_number = Column(Integer)  # TODO unique

    @property
    def groups(self):
        return [x.group for x in self.group_consultants]
