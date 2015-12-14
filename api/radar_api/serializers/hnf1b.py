from radar_api.serializers.meta import MetaSerializerMixin
from radar.serializers.models import ModelSerializer
from radar.models.hnf1b import Hnf1bClinicalPicture, TYPES_OF_DIABETES
from radar.serializers.codes import CodedStringSerializer
from radar_api.serializers.patient_mixins import PatientSerializerMixin


class Hnf1bClinicalPictureSerializer(PatientSerializerMixin, MetaSerializerMixin, ModelSerializer):
    type_of_diabetes = CodedStringSerializer(TYPES_OF_DIABETES)

    class Meta(object):
        model_class = Hnf1bClinicalPicture
