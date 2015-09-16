from radar.api.serializers.data_sources import DataSourceSerializerMixin
from radar.api.serializers.meta import MetaSerializerMixin
from radar.api.serializers.patients import PatientSerializerMixin
from radar.lib.serializers import ReferenceField, ModelSerializer
from radar.lib.models import Disorder, Comorbidity


class DisorderSerializer(ModelSerializer):
    class Meta(object):
        model_class = Disorder


class DisorderReferenceField(ReferenceField):
    model_class = Disorder
    serializer_class = DisorderSerializer


class ComorbiditySerializer(MetaSerializerMixin, PatientSerializerMixin, DataSourceSerializerMixin, ModelSerializer):
    disorder = DisorderReferenceField()

    class Meta(object):
        model_class = Comorbidity
        exclude = ['disorder_id']