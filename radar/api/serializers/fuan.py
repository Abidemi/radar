from cornflake import fields
from cornflake.sqlalchemy_orm import ModelSerializer
from cornflake.validators import max_length, none_if_blank, optional

from radar.api.serializers.common import IntegerLookupField, MetaMixin, PatientMixin, StringLookupField
from radar.api.serializers.validators import valid_date_for_patient
from radar.models.fuan import FuanClinicalPicture, RELATIVES, THP_RESULTS


class FuanClinicalPictureSerializer(PatientMixin, MetaMixin, ModelSerializer):
    picture_date = fields.DateField()
    gout = fields.BooleanField(required=False)
    gout_date = fields.DateField(required=False)
    family_gout = fields.BooleanField(required=False)
    family_gout_relatives = fields.ListField(required=False, child=IntegerLookupField(RELATIVES))
    thp = StringLookupField(THP_RESULTS, required=False)
    uti = fields.BooleanField(required=False)
    comments = fields.StringField(required=False, validators=[none_if_blank(), optional(), max_length(10000)])

    def pre_validate(self, data):
        if not data['gout']:
            data['gout_date'] = None

        if not data['family_gout']:
            data['family_gout_relatives'] = []

        return data

    class Meta(object):
        model_class = FuanClinicalPicture
        validators = [
            valid_date_for_patient('picture_date'),
            valid_date_for_patient('gout_date')
        ]
