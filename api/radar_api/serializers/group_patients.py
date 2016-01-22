from radar_api.serializers.meta import MetaSerializerMixin
from radar_api.serializers.groups import GroupReferenceField
from radar_api.serializers.patient_mixins import PatientSerializerMixin
from radar.models.groups import GroupPatient
from radar.serializers.models import ModelSerializer
from radar.serializers.fields import BooleanField


class GroupPatientSerializer(PatientSerializerMixin, MetaSerializerMixin, ModelSerializer):
    group = GroupReferenceField()
    created_group = GroupReferenceField()
    current = BooleanField(read_only=True)

    class Meta(object):
        model_class = GroupPatient
        exclude = ['group_id', 'created_group_id']
