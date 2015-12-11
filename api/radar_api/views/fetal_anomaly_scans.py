from radar_api.serializers.fetal_anomaly_scans import FetalAnomalyScanSerializer
from radar.models.fetal_anomaly_scans import FetalAnomalyScan
from radar.validation.fetal_anomaly_scans import FetalAnomalyScanValidation
from radar.views.data_sources import DataSourceObjectViewMixin
from radar.views.patients import PatientObjectDetailView, PatientObjectListView


class FetalAnomalyScanListView(DataSourceObjectViewMixin, PatientObjectListView):
    serializer_class = FetalAnomalyScanSerializer
    model_class = FetalAnomalyScan
    validation_class = FetalAnomalyScanValidation


class FetalAnomalyScanDetailView(DataSourceObjectViewMixin, PatientObjectDetailView):
    serializer_class = FetalAnomalyScanSerializer
    model_class = FetalAnomalyScan
    validation_class = FetalAnomalyScanValidation


def register_views(app):
    app.add_url_rule('/fetal-anomaly-scans', view_func=FetalAnomalyScanListView.as_view('fetal_anomaly_scan_list'))
    app.add_url_rule('/fetal-anomaly-scans/<id>', view_func=FetalAnomalyScanDetailView.as_view('fetal_anomaly_scan_detail'))
