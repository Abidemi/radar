from cornflake import serializers
from cornflake import fields

from radar.api.serializers.common import GroupField


class DataPointSerializer(serializers.Serializer):
    date = fields.DateField()
    new_patients = fields.IntegerField()
    total_patients = fields.IntegerField()


class DataPointListSerializer(serializers.Serializer):
    points = fields.ListField(child=DataPointSerializer())


class PatientsByGroupSerializer(serializers.Serializer):
    group = GroupField()
    count = fields.IntegerField()


class PatientsByGroupListSerializer(serializers.Serializer):
    counts = fields.ListField(child=PatientsByGroupSerializer())
