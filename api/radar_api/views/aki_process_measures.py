from sqlalchemy import case, null, func, true, and_, or_
from flask import request

from radar_api.serializers.aki_process_measures import (
    AkiProcessMeasuresSerializer,
    AkiProcessMeasureStatsSerializer,
    AkiProcessMeasureStatsRequestSerializer
)
from radar.models.aki_process_measures import AkiProcessMeasures, PROCESS_MEASURES
from radar.validation.aki_process_measures import AkiProcessMeasuresValidation
from radar.views.patients import PatientObjectListView, PatientObjectDetailView
from radar.views.sources import SourceObjectViewMixin
from radar.views.core import response_json, ApiView
from radar.database import db


class AkiProcessMeasuresListView(SourceObjectViewMixin, PatientObjectListView):
    serializer_class = AkiProcessMeasuresSerializer
    model_class = AkiProcessMeasures
    validation_class = AkiProcessMeasuresValidation


class AkiProcessMeasuresDetailView(SourceObjectViewMixin, PatientObjectDetailView):
    serializer_class = AkiProcessMeasuresSerializer
    model_class = AkiProcessMeasures
    validation_class = AkiProcessMeasuresValidation


def get_col(process_measure):
    return getattr(AkiProcessMeasures, process_measure)


def get_numerator_label(name):
    return '%s_numerator' % name


def get_denominator_label(name):
    return '%s_denominator' % name


def get_numerator_col(process_measure):
    """Number of patients where the patient received the process measure (true)."""

    col = get_col(process_measure)
    label = get_numerator_label(process_measure)

    return func.coalesce(func.sum(case(
        [(col == true(), 1)],
        else_=0
    )), 0).label(label)


def get_denominator_col(process_measure):
    """Number of patients where the patient was eligible for the process measure (not null)."""

    col = get_col(process_measure)
    label = get_denominator_label(process_measure)

    return func.coalesce(func.sum(case(
        [(col != null(), 1)],
        else_=0
    )), 0).label(label)


def get_cqs_numerator_col(process_measures):
    """Total number of process measures received (true)."""

    cols = [get_numerator_col(x) for x in process_measures]
    label = get_numerator_label('cqs')

    return sum(cols).label(label)


def get_cqs_denominator_col(process_measures):
    """Total number of process measures that were eligible (not null)."""

    cols = [get_denominator_col(x) for x in process_measures]
    label = get_denominator_label('cqs')

    return sum(cols).label(label)


def get_acs_numerator_col(process_measures):
    """Number of patients where all of the eligible process measures were received (all true or null)."""

    cols = [get_col(x) for x in process_measures]
    label = get_numerator_label('acs')

    return func.coalesce(func.sum(
        case(
            [(and_(or_(x == true(), x == null()) for x in cols), 1)],
            else_=0
        )
    ), 0).label(label)


def get_acs_denominator_col(process_measures):
    """Number of patients."""

    label = get_denominator_label('acs')

    return func.count().label(label)


class AkiProcessMeasureStatsView(ApiView):
    """
    Each process measure has a numerator and denominator. The numerator is the
    number of patients who received the measure and the denominator is the number
    of patients who were eligible for this measure.

    Composite Quality Score (CQS) - sum of measure numerators divided by sum of
    measure denominators. See: http://www.wchq.org/reporting/documents/CMS_Composite_Score.pdf

    Appropriate Care Score (ACS) - number of patients who received all measures
    they were eligible before divided by the total number of patients. See:
    http://www.advancingqualitynw.nhs.uk/faqs/#how-score-is-calculated
    """

    @response_json(AkiProcessMeasureStatsSerializer)
    def get(self):
        serializer = AkiProcessMeasureStatsRequestSerializer()
        args = serializer.args_to_value(request.args)
        group = args.get('group')

        cols = []
        cols.extend([get_numerator_col(x) for x in PROCESS_MEASURES])
        cols.extend([get_denominator_col(x) for x in PROCESS_MEASURES])
        cols.append(get_cqs_numerator_col(PROCESS_MEASURES))
        cols.append(get_cqs_denominator_col(PROCESS_MEASURES))
        cols.append(get_acs_numerator_col(PROCESS_MEASURES))
        cols.append(get_acs_denominator_col(PROCESS_MEASURES))

        q = db.session.query(*cols)

        if group is not None:
            q = q.filter(AkiProcessMeasures.source_group == group)

        row = q.one()

        names = list(PROCESS_MEASURES)
        names.extend(['cqs', 'acs'])
        stats = {}

        for name in names:
            stats[name] = (
                getattr(row, get_numerator_label(name)),
                getattr(row, get_denominator_label(name)),
            )

        return stats


def register_views(app):
    app.add_url_rule('/aki-process-measures', view_func=AkiProcessMeasuresListView.as_view('aki_process_measures_list'))
    app.add_url_rule('/aki-process-measures/<id>', view_func=AkiProcessMeasuresDetailView.as_view('aki_process_measures_detail'))
    app.add_url_rule('/aki-process-measure-stats', view_func=AkiProcessMeasureStatsView.as_view('aki_process_measure_stats'))
