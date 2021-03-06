from cornflake import fields
from cornflake import serializers
from cornflake.exceptions import ValidationError
from cornflake.sqlalchemy_orm import ModelSerializer, ReferenceField
from cornflake.validators import email_address, lower, max_length, none_if_blank, not_empty, optional, upper

from radar.api.serializers.common import GroupField, MetaMixin, PatientMixin
from radar.api.serializers.validators import gmc_number
from radar.database import db
from radar.models.consultants import Consultant, GroupConsultant, Specialty
from radar.models.groups import GROUP_TYPE
from radar.models.patient_consultants import PatientConsultant


class SpecialtySerializer(ModelSerializer):
    class Meta(object):
        model_class = Specialty


class SpeciailtyField(ReferenceField):
    model_class = Specialty
    serializer_class = SpecialtySerializer


class ChildGroupConsultantSerializer(ModelSerializer):
    group = GroupField()

    class Meta(object):
        model_class = GroupConsultant
        exclude = ['id', 'consultant_id', 'group_id']

    def validate_group(self, group):
        # Consultants can only be added to hospitals
        if group.type != GROUP_TYPE.HOSPITAL:
            raise ValidationError('Must be a hospital.')

        return group


class GroupConsultantListSerializer(serializers.ListSerializer):
    child = ChildGroupConsultantSerializer()

    def validate(self, group_consultants):
        # Check the consultant isn't in the same group multiple times.

        groups = set()

        for i, group_consultant in enumerate(group_consultants):
            group = group_consultant['group']

            if group in groups:
                raise ValidationError({i: {'group': 'Consultant already in group.'}})
            else:
                groups.add(group)

        return group_consultants


# TODO check GMC number not duplicated
class ConsultantSerializer(ModelSerializer):
    first_name = fields.StringField(validators=[not_empty(), upper(), max_length(100)])
    last_name = fields.StringField(validators=[not_empty(), upper(), max_length(100)])
    email = fields.StringField(required=False, validators=[none_if_blank(), optional(), lower(), email_address()])
    telephone_number = fields.StringField(required=False, validators=[none_if_blank(), optional(), max_length(100)])
    gmc_number = fields.StringField(required=False, validators=[gmc_number()])
    groups = GroupConsultantListSerializer(source='group_consultants')
    specialty = SpeciailtyField()

    class Meta(object):
        model_class = Consultant
        exclude = ['specialty_id']

    def _save(self, instance, data):
        # Custom save method so we can create the group_consultant records too.

        instance.first_name = data['first_name']
        instance.last_name = data['last_name']
        instance.email = data['email']
        instance.telephone_number = data['telephone_number']
        instance.gmc_number = data['gmc_number']
        instance.specialty = data['specialty']
        instance.group_consultants = self.fields['groups'].create(data['group_consultants'])

    def create(self, data):
        instance = Consultant()
        self._save(instance, data)
        return instance

    def update(self, instance, data):
        # Unique constraint fails unless we flush the deletes before the inserts
        instance.group_consultants = []
        db.session.flush()

        self._save(instance, data)

        return instance


class ChildConsultantSerializer(ModelSerializer):
    specialty = SpeciailtyField()

    class Meta(object):
        model_class = Consultant
        exclude = ['specialty_id']


class ConsultantField(ReferenceField):
    model_class = Consultant
    serializer_class = ChildConsultantSerializer


class GroupConsultantSerializer(ModelSerializer):
    group = GroupField()
    consultant = ConsultantField()

    class Meta(object):
        model_class = GroupConsultant
        exclude = ['group_id', 'consultant_id']


class PatientConsultantSerializer(PatientMixin, MetaMixin, ModelSerializer):
    from_date = fields.DateField()
    to_date = fields.DateField(required=False)
    consultant = ConsultantField()

    class Meta(object):
        model_class = PatientConsultant
        exclude = ['consultant_id']

    def validate(self, data):
        data = super(PatientConsultantSerializer, self).validate(data)

        # Check to date is after from date
        if data['to_date'] is not None and data['to_date'] < data['from_date']:
            raise ValidationError({'to_date': 'Must be on or after from date.'})

        return data
