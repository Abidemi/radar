from radar_api.serializers.dialysis import DialysisSerializer
from radar.validation.dialysis import DialysisValidation
from radar.models import Dialysis, DIALYSIS_MODALITIES
from radar.views.data_sources import DataSourceObjectViewMixin
from radar.views.patients import PatientObjectDetailView, PatientObjectListView
from radar.views.codes import CodedIntegerListView


class DialysisListView(DataSourceObjectViewMixin, PatientObjectListView):
    serializer_class = DialysisSerializer
    validation_class = DialysisValidation
    model_class = Dialysis


class DialysisDetailView(DataSourceObjectViewMixin, PatientObjectDetailView):
    serializer_class = DialysisSerializer
    validation_class = DialysisValidation
    model_class = Dialysis


class DialysisModalityListView(CodedIntegerListView):
    items = DIALYSIS_MODALITIES


def register_views(app):
    app.add_url_rule('/dialysis', view_func=DialysisListView.as_view('dialysis_list'))
    app.add_url_rule('/dialysis/<id>', view_func=DialysisDetailView.as_view('dialysis_detail'))
    app.add_url_rule('/dialysis-modalities', view_func=DialysisModalityListView.as_view('dialysis_modality_list'))
