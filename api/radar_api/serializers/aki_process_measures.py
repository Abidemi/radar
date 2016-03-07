from radar_api.serializers.meta import MetaSerializerMixin
from radar.serializers.models import ModelSerializer
from radar.models.aki_process_measures import AkiProcessMeasures
from radar_api.serializers.patient_mixins import PatientSerializerMixin
from radar_api.serializers.sources import SourceSerializerMixin
from radar.serializers.core import Serializer
from radar.serializers.fields import IntegerField, ListField
from radar_api.serializers.groups import GroupReferenceField


class AkiProcessMeasuresSerializer(PatientSerializerMixin, SourceSerializerMixin, MetaSerializerMixin, ModelSerializer):
    class Meta(object):
        model_class = AkiProcessMeasures


class FractionSerializer(ListField):
    def __init__(self, **kwargs):
        super(FractionSerializer, self).__init__(IntegerField(), **kwargs)


class AkiProcessMeasureStatsSerializer(Serializer):
    dipstick_urinalysis = FractionSerializer()
    medication_review = FractionSerializer()
    uss = FractionSerializer()
    senior_review = FractionSerializer()
    self_management = FractionSerializer()
    physiological_monitoring = FractionSerializer()
    ue_admission = FractionSerializer()
    ue_repeated = FractionSerializer()

    # Composite Quality Score (CQS)
    cqs = FractionSerializer()

    # Appropriate Care Score (ACS)
    acs = FractionSerializer()


class AkiProcessMeasureStatsRequestSerializer(Serializer):
    group = GroupReferenceField()
