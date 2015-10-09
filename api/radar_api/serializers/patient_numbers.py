from radar_api.serializers.data_sources import DataSourceSerializerMixin
from radar_api.serializers.meta import MetaSerializerMixin
from radar_api.serializers.organisations import OrganisationReferenceField
from radar_api.serializers.patient_mixins import PatientSerializerMixin
from radar.serializers.models import ModelSerializer
from radar.models import PatientNumber


class PatientNumberSerializer(PatientSerializerMixin, DataSourceSerializerMixin, MetaSerializerMixin, ModelSerializer):
    organisation = OrganisationReferenceField()

    class Meta(object):
        model_class = PatientNumber
        exclude = ['organisation_id']
