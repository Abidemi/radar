from cornflake import fields, serializers

from radar.api.serializers.diagnoses import DiagnosisSerializer, PatientDiagnosisSerializer
from radar.api.views.common import (
    IntegerLookupListView,
    SourceObjectViewMixin,
    PatientObjectDetailView,
    PatientObjectListView
)
from radar.api.views.generics import ListModelView, parse_args
from radar.models.diagnoses import Diagnosis, PatientDiagnosis, BIOPSY_DIAGNOSES, GroupDiagnosis, GROUP_DIAGNOSIS_TYPE


class DiagnosisRequestSerializer(serializers.Serializer):
    primary_group = fields.CommaSeparatedField(child=fields.IntegerField(), required=False)
    secondary_group = fields.CommaSeparatedField(child=fields.IntegerField(), required=False)


class PatientDiagnosisRequestSerializer(serializers.Serializer):
    primary_group = fields.CommaSeparatedField(child=fields.IntegerField(), required=False)
    secondary_group = fields.CommaSeparatedField(child=fields.IntegerField(), required=False)


def patient_diagnosis_group_type_filter(group_ids, group_diagnosis_type):
    return _diagnosis_group_type_filter(PatientDiagnosis.diagnosis_id, group_ids, group_diagnosis_type)


def diagnosis_group_type_filter(group_ids, group_diagnosis_type):
    return _diagnosis_group_type_filter(Diagnosis.id, group_ids, group_diagnosis_type)


def _diagnosis_group_type_filter(diagnois_column, group_ids, group_diagnosis_type):
    return GroupDiagnosis.query\
        .filter(GroupDiagnosis.group_id.in_(group_ids))\
        .filter(GroupDiagnosis.diagnosis_id == diagnois_column)\
        .filter(GroupDiagnosis.type == group_diagnosis_type)\
        .exists()


class PatientDiagnosisListView(SourceObjectViewMixin, PatientObjectListView):
    serializer_class = PatientDiagnosisSerializer
    model_class = PatientDiagnosis

    def filter_query(self, query):
        query = super(PatientDiagnosisListView, self).filter_query(query)

        args = parse_args(PatientDiagnosisRequestSerializer)

        primary_group_ids = args['primary_group']
        secondary_group_ids = args['secondary_group']

        if primary_group_ids:
            query = query.filter(patient_diagnosis_group_type_filter(primary_group_ids, GROUP_DIAGNOSIS_TYPE.PRIMARY))

        if secondary_group_ids:
            query = query.filter(patient_diagnosis_group_type_filter(secondary_group_ids, GROUP_DIAGNOSIS_TYPE.SECONDARY))

        return query


class PatientDiagnosisDetailView(SourceObjectViewMixin, PatientObjectDetailView):
    serializer_class = PatientDiagnosisSerializer
    model_class = PatientDiagnosis


class DiagnosisListView(ListModelView):
    serializer_class = DiagnosisSerializer
    model_class = Diagnosis

    def filter_query(self, query):
        query = super(DiagnosisListView, self).filter_query(query)

        args = parse_args(DiagnosisRequestSerializer)

        primary_group_ids = args['primary_group']
        secondary_group_ids = args['secondary_group']

        if primary_group_ids:
            query = query.filter(diagnosis_group_type_filter(primary_group_ids, GROUP_DIAGNOSIS_TYPE.PRIMARY))

        if secondary_group_ids:
            query = query.filter(diagnosis_group_type_filter(secondary_group_ids, GROUP_DIAGNOSIS_TYPE.SECONDARY))

        return query


class BiopsyDiagnosisListView(IntegerLookupListView):
    items = BIOPSY_DIAGNOSES


def register_views(app):
    app.add_url_rule('/patient-diagnoses', view_func=PatientDiagnosisListView.as_view('patient_diagnosis_list'))
    app.add_url_rule('/patient-diagnoses/<id>', view_func=PatientDiagnosisDetailView.as_view('patient_diagnosis_detail'))
    app.add_url_rule('/diagnoses', view_func=DiagnosisListView.as_view('diagnosis_list'))
    app.add_url_rule('/biopsy-diagnoses', view_func=BiopsyDiagnosisListView.as_view('biopsy_diagnosis_list'))
