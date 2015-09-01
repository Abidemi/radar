from radar.lib.serializers import MetaSerializerMixin, ModelSerializer
from radar.lib.views import ListCreateApiView, RetrieveUpdateDestroyAPIView
from radar.models import Facility


class FacilitySerializer(MetaSerializerMixin, ModelSerializer):
    class Meta:
        model_class = Facility


class FacilityList(ListCreateApiView):
    serializer_class = FacilitySerializer
    model_class = Facility


class FacilityDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = FacilitySerializer
    model_class = Facility
