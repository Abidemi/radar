from cornflake.sqlalchemy_orm import ModelSerializer, ReferenceField
from cornflake import fields
from cornflake import serializers
from cornflake.validators import none_if_blank, optional, max_length, min_length
from cornflake.exceptions import ValidationError

from radar.api.serializers.common import (
    PatientMixin,
    SourceMixin,
    MetaMixin,
    IntegerLookupField,
    GroupField,
    EnumLookupField
)
from radar.api.serializers.validators import valid_date_for_patient
from radar.database import db
from radar.models.diagnoses import (
    Diagnosis,
    PatientDiagnosis,
    BIOPSY_DIAGNOSES,
    GROUP_DIAGNOSIS_TYPE,
    GROUP_DIAGNOSIS_TYPE_NAMES,
    GroupDiagnosis
)


class GroupDiagnosisSerializer(ModelSerializer):
    group = GroupField()
    type = EnumLookupField(GROUP_DIAGNOSIS_TYPE, GROUP_DIAGNOSIS_TYPE_NAMES)

    class Meta(object):
        model_class = GroupDiagnosis
        exclude = ['id', 'group_id', 'diagnosis_id']


class GroupDiagnosisListSerializer(serializers.ListSerializer):
    child = GroupDiagnosisSerializer()

    def validate(self, group_diagnoses):
        groups = set()

        for i, group_diagnosis in enumerate(group_diagnoses):
            group = group_diagnosis['group']

            if group in groups:
                raise ValidationError({i: {'group': 'Duplicate group.'}})
            else:
                groups.add(group)

        return group_diagnoses


class DiagnosisSerializer(ModelSerializer):
    name = fields.StringField(validators=[min_length(1), max_length(1000)])
    groups = GroupDiagnosisListSerializer(source='group_diagnoses')
    retired = fields.BooleanField()

    class Meta(object):
        model_class = Diagnosis

    def _save(self, instance, data):
        instance.name = data['name']
        instance.retired = data['retired']
        instance.group_diagnoses = self.fields['groups'].create(data['group_diagnoses'])

    def create(self, data):
        instance = Diagnosis()
        self._save(instance, data)
        return instance

    def update(self, instance, data):
        # Unique constraint fails unless we flush the deletes before the inserts
        instance.group_diagnoses = []
        db.session.flush()

        self._save(instance, data)

        return instance


class TinyDiagnosisSerializer(ModelSerializer):
    class Meta(object):
        model_class = Diagnosis


class DiagnosisField(ReferenceField):
    model_class = Diagnosis
    serializer_class = TinyDiagnosisSerializer


class PatientDiagnosisSerializer(PatientMixin, SourceMixin, MetaMixin, ModelSerializer):
    diagnosis = DiagnosisField(required=False)
    diagnosis_text = fields.StringField(required=False, validators=[none_if_blank(), optional(), max_length(1000)])
    symptoms_date = fields.DateField(required=False)
    symptoms_age = fields.IntegerField(read_only=True)
    from_date = fields.DateField()
    from_age = fields.IntegerField(read_only=True)
    to_date = fields.DateField(required=False)
    to_age = fields.IntegerField(read_only=True)
    gene_test = fields.BooleanField(required=False)
    biochemistry = fields.BooleanField(required=False)
    clinical_picture = fields.BooleanField(required=False)
    biopsy = fields.BooleanField(required=False)
    biopsy_diagnosis = IntegerLookupField(BIOPSY_DIAGNOSES, required=False)
    comments = fields.StringField(required=False, validators=[none_if_blank(), optional(), max_length(10000)])

    class Meta(object):
        model_class = PatientDiagnosis
        exclude = ['diagnosis_id']
        validators = [
            valid_date_for_patient('symptoms_date'),
            valid_date_for_patient('from_date'),
            valid_date_for_patient('to_date'),
        ]

    def pre_validate(self, data):
        if data['diagnosis'] is not None:
            data['diagnosis_text'] = None

        if not data['biopsy']:
            data['biopsy_diagnosis'] = None

        return data

    def validate_diagnosis(self, diagnosis):
        if diagnosis.retired:
            raise ValidationError('Diagnosis has been retired, please choose another diagnosis.')

        return diagnosis

    def validate(self, data):
        if data['diagnosis'] is None and data['diagnosis_text'] is None:
            raise ValidationError({
                'diagnosis': 'Must specify a diagnosis.',
                'diagnosis_text': 'Must specify a diagnosis.',
            })

        # symptoms_date <= from_date <= to_date

        if data['symptoms_date'] is not None and data['from_date'] < data['symptoms_date']:
            raise ValidationError({'from_date': 'Must be on or after date of onset of symptoms.'})

        if data['to_date'] is not None and data['to_date'] < data['from_date']:
            raise ValidationError({'to_date': 'Must be on or after from date.'})

        return data
