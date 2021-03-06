from radar.api.serializers.transplants import TransplantSerializer
from radar.api.views.common import (
    IntegerLookupListView,
    PatientObjectDetailView,
    PatientObjectListView,
    SourceObjectViewMixin,
)
from radar.models.transplants import Transplant, TRANSPLANT_MODALITIES


class TransplantListView(SourceObjectViewMixin, PatientObjectListView):
    serializer_class = TransplantSerializer
    model_class = Transplant


class TransplantDetailView(SourceObjectViewMixin, PatientObjectDetailView):
    serializer_class = TransplantSerializer
    model_class = Transplant


class TransplantModalityListView(IntegerLookupListView):
    items = TRANSPLANT_MODALITIES


def register_views(app):
    app.add_url_rule('/transplants', view_func=TransplantListView.as_view('transplant_list'))
    app.add_url_rule('/transplants/<id>', view_func=TransplantDetailView.as_view('transplant_detail'))
    app.add_url_rule('/transplant-modalities', view_func=TransplantModalityListView.as_view('transplant_modality_list'))
