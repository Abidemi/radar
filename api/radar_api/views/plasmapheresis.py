from radar_api.serializers.plasmapheresis import PlasmapheresisSerializer
from radar.models import Plasmapheresis, PLASMAPHERESIS_RESPONSES, PLASMAPHERESIS_NO_OF_EXCHANGES
from radar.validation.plasmapheresis import PlasmapheresisValidation
from radar.views.codes import CodedStringListView
from radar.views.sources import SourceGroupObjectViewMixin
from radar.views.patients import PatientObjectListView, PatientObjectDetailView


class PlasmapheresisListView(SourceGroupObjectViewMixin, PatientObjectListView):
    serializer_class = PlasmapheresisSerializer
    model_class = Plasmapheresis
    validation_class = PlasmapheresisValidation


class PlasmapheresisDetailView(SourceGroupObjectViewMixin, PatientObjectDetailView):
    serializer_class = PlasmapheresisSerializer
    model_class = Plasmapheresis
    validation_class = PlasmapheresisValidation


class PlasmapheresisResponseListView(CodedStringListView):
    items = PLASMAPHERESIS_RESPONSES


class PlasmapheresisNoOfExchangesListView(CodedStringListView):
    items = PLASMAPHERESIS_NO_OF_EXCHANGES


def register_views(app):
    app.add_url_rule('/plasmapheresis', view_func=PlasmapheresisListView.as_view('plasmapheresis_list'))
    app.add_url_rule('/plasmapheresis/<id>', view_func=PlasmapheresisDetailView.as_view('plasmapheresis_detail'))
    app.add_url_rule('/plasmapheresis-responses', view_func=PlasmapheresisResponseListView.as_view('plasmapheresis_response_list'))
    app.add_url_rule('/plasmapheresis-no-of-exchanges', view_func=PlasmapheresisNoOfExchangesListView.as_view('plasmapheresis_no_of_exchanges_list'))
