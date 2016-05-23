from cornflake import fields, serializers
from cornflake.sqlalchemy_orm import ModelSerializer

from radar.api.serializers.common import (
    MetaMixin,
    SourceMixin,
    PatientMixin
)
from radar.models.aki_process_measures import AkiProcessMeasures, PROCESS_MEASURES


class _AkiProcessMeasuresSerializer(PatientMixin, SourceMixin, MetaMixin, ModelSerializer):
    date = fields.DateField()

    class Meta(object):
        model_class = AkiProcessMeasures


attrs = {field_name: fields.BooleanField(required=False) for field_name in PROCESS_MEASURES}
AkiProcessMeasuresSerializer = type('AkiProcessMeasuresSerializer', (_AkiProcessMeasuresSerializer,), attrs)


class FractionSerializer(fields.ListField):
    child = fields.IntegerField()


class AkiProcessMeasureStatsSerializer(serializers.Serializer):
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
