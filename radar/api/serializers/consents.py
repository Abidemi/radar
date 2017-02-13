from cornflake import fields, serializers
from cornflake.sqlalchemy_orm import ModelSerializer, ReferenceField
from cornflake.validators import max_length, none_if_blank, optional

from radar.api.serializers.common import (
    CohortGroupMixin,
    IntegerLookupField,
    MetaMixin,
    PatientMixin,
)
from radar.database import db
from radar.models.consents import Consent
from radar.models.patients import Patient


class ConsentSerializer(PatientMixin, CohortGroupMixin, MetaMixin, ModelSerializer):

    class Meta(object):
        model_class = Consent
