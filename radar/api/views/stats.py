from cornflake import fields, serializers
from cornflake.validators import in_
from flask import Blueprint

from radar.api.serializers.common import GroupField
from radar.api.serializers.stats import DataPointListSerializer, PatientsByGroupListSerializer, PatientsByGroupDateListSerializer
from radar.api.views.generics import response_json, ApiView, parse_args
from radar.models.groups import Group, GROUP_TYPE
from radar.stats import (
    patients_by_recruitment_date,
    patients_by_group,
    patients_by_group_date,
    patients_by_recruitment_group,
    patients_by_recruitment_group_date,
)


class PatientsByRecruitmentDateRequestSerializer(serializers.Serializer):
    group = GroupField(required=False)
    interval = fields.StringField(default='month', validators=[in_(['month'])])


class PatientsByGroupRequestSerializer(serializers.Serializer):
    group = GroupField(required=False)
    group_type = fields.EnumField(GROUP_TYPE, required=False)


class PatientsByGroupDateRequestSerializer(serializers.Serializer):
    group_type = fields.EnumField(GROUP_TYPE, required=False)
    interval = fields.StringField(default='month', validators=[in_('month')])


class PatientsByRecruitmentGroupRequestSerializer(serializers.Serializer):
    group = GroupField(required=False)


class PatientsByRecruitmentGroupDateRequestSerializer(serializers.Serializer):
    group = GroupField(required=False)
    interval = fields.StringField(default='month', validators=[in_('month')])


class PatientsByRecruitmentDateView(ApiView):
    """
    Number of patients recruited over time.
    """

    @response_json(DataPointListSerializer)
    def get(self):
        args = parse_args(PatientsByRecruitmentDateRequestSerializer)

        if args['group'] is not None:
            group = args['group']
        else:
            group = Group.get_radar()

        points = patients_by_recruitment_date(group, args['interval'])

        return {'points': points}


class PatientsByGroupView(ApiView):
    """
    Number of patients in each group.
    """

    @response_json(PatientsByGroupListSerializer)
    def get(self):
        args = parse_args(PatientsByGroupRequestSerializer)

        counts = patients_by_group(args['group'], args['group_type'])
        counts = [{'group': group, 'count': count} for group, count in counts]

        return {'counts': counts}


class PatientsByGroupDateView(ApiView):
    """
    Number of patients in each group over time.
    """

    @response_json(PatientsByGroupDateListSerializer)
    def get(self):
        args = parse_args(PatientsByGroupDateRequestSerializer)

        results = patients_by_group_date(args['group_type'], args['interval'])

        return results


class PatientsByRecruitmentGroupView(ApiView):
    """
    Number of patients recruited by each group.
    """

    @response_json(PatientsByGroupListSerializer)
    def get(self):
        args = parse_args(PatientsByRecruitmentGroupRequestSerializer)

        if args['group'] is not None:
            group = args['group']
        else:
            group = Group.get_radar()

        counts = patients_by_recruitment_group(group)
        counts = [{'group': x, 'count': y} for x, y in counts]

        return {'counts': counts}


class PatientsByRecruitmentGroupDateView(ApiView):
    """
    Number of patients recruited by each group over time.
    """

    @response_json(PatientsByGroupDateListSerializer)
    def get(self):
        args = parse_args(PatientsByRecruitmentGroupDateRequestSerializer)

        if args['group'] is not None:
            group = args['group']
        else:
            group = Group.get_radar()

        results = patients_by_recruitment_group_date(group, args['interval'])

        return results


def register_views(app):
    stats = Blueprint('stats', __name__)
    stats.add_url_rule('/patients-by-recruitment-date', view_func=PatientsByRecruitmentDateView.as_view('patients_by_recruitment_date'))
    stats.add_url_rule('/patients-by-group', view_func=PatientsByGroupView.as_view('patients_by_group'))
    stats.add_url_rule('/patients-by-group-date', view_func=PatientsByGroupDateView.as_view('patients_by_group_date'))
    stats.add_url_rule('/patients-by-recruitment-group', view_func=PatientsByRecruitmentGroupView.as_view('patients_by_recruitment_group'))
    stats.add_url_rule('/patients-by-recruitment-group-date', view_func=PatientsByRecruitmentGroupDateView.as_view('patients_by_recruitment_group_date'))
    app.register_blueprint(stats, url_prefix='/stats')
