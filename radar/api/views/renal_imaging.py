from radar.lib.serializers import MetaSerializerMixin, FacilitySerializerMixin, ModelSerializer
from radar.lib.views import FacilityDataMixin, PatientDataList, PatientDataDetail
from radar.models import RenalImaging


class RenalImagingSerializer(MetaSerializerMixin, FacilitySerializerMixin, ModelSerializer):
    class Meta:
        model_class = RenalImaging


class RenalImagingList(FacilityDataMixin, PatientDataList):
    serializer_class = RenalImagingSerializer
    model_class = RenalImaging


class RenalImagingDetail(FacilityDataMixin, PatientDataDetail):
    serializer_class = RenalImagingSerializer
    model_class = RenalImaging
