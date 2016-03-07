from radar_api.serializers.aki_process_measures import AkiProcessMeasuresSerializer
from radar.models.aki_process_measures import AkiProcessMeasures
from radar.validation.aki_process_measures import AkiProcessMeasuresValidation
from radar.views.patients import PatientObjectListView, PatientObjectDetailView


class AkiProcessMeasuresListView(PatientObjectListView):
    serializer_class = AkiProcessMeasuresSerializer
    model_class = AkiProcessMeasures
    validation_class = AkiProcessMeasuresValidation


class AkiProcessMeasuresDetailView(PatientObjectDetailView):
    serializer_class = AkiProcessMeasuresSerializer
    model_class = AkiProcessMeasures
    validation_class = AkiProcessMeasuresValidation


def register_views(app):
    app.add_url_rule('/aki-process-measures', view_func=AkiProcessMeasuresListView.as_view('aki_process_measures_list'))
    app.add_url_rule('/aki-process-measures/<id>', view_func=AkiProcessMeasuresDetailView.as_view('aki_process_measures_detail'))
