from radar.api.serializers.patient_numbers import PatientNumberSerializer
from radar.api.views.common import (
    RadarObjectViewMixin,
    PatientObjectDetailView,
    PatientObjectListView,
    DemographicsViewMixin
)
from radar.models.patient_numbers import PatientNumber


class PatientNumberListView(RadarObjectViewMixin, DemographicsViewMixin, PatientObjectListView):
    serializer_class = PatientNumberSerializer
    model_class = PatientNumber


class PatientNumberDetailView(RadarObjectViewMixin, DemographicsViewMixin, PatientObjectDetailView):
    serializer_class = PatientNumberSerializer
    model_class = PatientNumber


def register_views(app):
    app.add_url_rule('/patient-numbers', view_func=PatientNumberListView.as_view('patient_number_list'))
    app.add_url_rule('/patient-numbers/<id>', view_func=PatientNumberDetailView.as_view('patient_number_detail'))