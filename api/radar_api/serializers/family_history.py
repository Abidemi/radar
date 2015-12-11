from radar_api.serializers.cohorts import CohortSerializerMixin
from radar_api.serializers.meta import MetaSerializerMixin
from radar_api.serializers.patient_mixins import PatientSerializerMixin
from radar.models.family_history import FamilyHistory, FamilyHistoryRelative, RELATIONSHIPS
from radar.serializers.core import Serializer
from radar.serializers.models import ModelSerializer, ReferenceField
from radar.serializers.fields import ListField, IntegerField
from radar.serializers.codes import CodedIntegerSerializer
from radar.models.patients import Patient


class PatientSerializer(Serializer):
    id = IntegerField()


class PatientReferenceField(ReferenceField):
    model_class = Patient
    serializer_class = PatientSerializer


class FamilyHistoryRelativeSerializer(ModelSerializer):
    relationship = CodedIntegerSerializer(RELATIONSHIPS)
    patient = PatientReferenceField()

    class Meta(object):
        model_class = FamilyHistoryRelative
        exclude = ['id']


class FamilyHistorySerializer(PatientSerializerMixin, CohortSerializerMixin, MetaSerializerMixin, ModelSerializer):
    relatives = ListField(FamilyHistoryRelativeSerializer())

    class Meta(object):
        model_class = FamilyHistory

    def create_relative(self, deserialized_data):
        relative = FamilyHistoryRelative()
        self.relatives.field.update(relative, deserialized_data)
        return relative

    def update(self, obj, deserialized_data):
        for attr, value in deserialized_data.items():
            if attr == 'relatives':
                obj.relatives = []

                for x in value:
                    relative = self.create_relative(x)
                    obj.relatives.append(relative)
            elif hasattr(obj, attr):
                setattr(obj, attr, value)

        return obj
