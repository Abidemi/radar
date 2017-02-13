from radar.api.serializers.consents import ConsentSerializer
from radar.api.views.common import (
    GroupObjectViewMixin,
    IntegerLookupListView,
    PatientObjectDetailView,
    PatientObjectListView
)
from radar.models.consents import Consent


class ConsentListView(GroupObjectViewMixin, PatientObjectListView):
    serializer_class = ConsentSerializer
    model_class = Consent


def register_views(app):
    app.add_url_rule('/patient-consents', view_func=ConsentListView.as_view('consent_list'))
    # app.add_url_rule('/family-histories/<id>', view_func=FamilyHistoryDetailView.as_view('family_history_detail'))
    # app.add_url_rule('/family-history-relationships', view_func=FamilyHistoryRelationshipListView.as_view('family_history_relationship_list'))
