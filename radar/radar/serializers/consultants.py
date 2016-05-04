from cornflake.sqlalchemy_orm import ModelSerializer, ReferenceField
from cornflake import fields
from cornflake import serializers
from cornflake.validators import not_empty, upper, max_length, none_if_blank, optional, lower, email_address
from cornflake.exceptions import ValidationError

from radar.serializers.validators import gmc_number
from radar.serializers.common import GroupField, MetaMixin, PatientMixin
from radar.models.consultants import Consultant, GroupConsultant, PatientConsultant
from radar.models.groups import GROUP_TYPE
from radar.database import db


class ChildGroupConsultantSerializer(MetaMixin, ModelSerializer):
    group = GroupField()

    class Meta(object):
        model_class = GroupConsultant
        exclude = ['id', 'consultant_id', 'group_id']

    def validate_group(self, group):
        if group.type != GROUP_TYPE.HOSPITAL:
            raise ValidationError('Must be a hospital.')

        return group


class GroupConsultantListSerializer(serializers.ListSerializer):
    child = ChildGroupConsultantSerializer

    def validate(self, group_consultants):
        groups = set()

        for i, group_consultant in enumerate(group_consultants):
            group = group_consultant.group

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
    group_consultants = GroupConsultantListSerializer()

    class Meta(object):
        model_class = Consultant

    def _save(self, instance, data):
        instance.first_name = data['first_name']
        instance.last_name = data['last_name']
        instance.email = data['email']
        instance.telephone_number = data['telephone_number']
        instance.gmc_number = data['gmc_number']
        instance.group_consultants = self.group_consultants.create(data['group_consultants'])

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


class ChildConsultantSerializer(MetaMixin, ModelSerializer):
    class Meta(object):
        model_class = Consultant


class ConsultantField(ReferenceField):
    model_class = Consultant
    serializer_class = ChildConsultantSerializer


class GroupConsultantSerializer(MetaMixin, ModelSerializer):
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

        if data['to_date'] is not None and data['to_date'] < data['from_date']:
            raise ValidationError({'to_date': 'Must be on or after from date.'})

        return data
