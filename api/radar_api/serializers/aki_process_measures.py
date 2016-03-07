from radar_api.serializers.meta import MetaSerializerMixin
from radar.serializers.models import ModelSerializer
from radar.models.aki_process_measures import AkiProcessMeasures
from radar_api.serializers.patient_mixins import PatientSerializerMixin


class AkiProcessMeasuresSerializer(PatientSerializerMixin, MetaSerializerMixin, ModelSerializer):
    class Meta(object):
        model_class = AkiProcessMeasures
