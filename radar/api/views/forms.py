from cornflake import serializers, fields
from sqlalchemy import func, or_
from cornflake.validators import in_

from radar.database import db
from radar.api.serializers.common import QueryPatientField
from radar.api.serializers.forms import (
    FormSerializer,
    EntrySerializer,
    FormCountSerializer
)
from radar.api.views.common import (
    PatientObjectDetailView,
    PatientObjectListView
)
from radar.api.views.generics import (
    ListView,
    ListModelView,
    RetrieveModelView,
    parse_args
)
from radar.models.forms import Entry, Form, GroupForm, GroupQuestionnaire


class FormListRequestSerializer(serializers.Serializer):
    patient = QueryPatientField(required=False)
    type = fields.StringField(required=False, validators=[in_(['form', 'questionnaire'])])
    slug = fields.StringField(required=False)


class FormCountListRequestSerializer(serializers.Serializer):
    patient = QueryPatientField(required=False)
    type = fields.StringField(required=False, validators=[in_(['form', 'questionnaire'])])


class EntryRequestSerializer(serializers.Serializer):
    form = fields.IntegerField(required=False)


def filter_by_patient_form(patient):
    group_ids = [x.id for x in patient.groups]

    return GroupForm.query\
        .filter(GroupForm.group_id.in_(group_ids))\
        .filter(GroupForm.form_id == Form.id)\
        .exists()


def filter_by_patient_questionnaire(patient):
    group_ids = [x.id for x in patient.groups]

    return GroupQuestionnaire.query\
        .filter(GroupQuestionnaire.group_id.in_(group_ids))\
        .filter(GroupQuestionnaire.form_id == Form.id)\
        .exists()


def filter_by_patient(patient, type=None):
    if type is None:
        return or_(filter_by_patient_form(patient), filter_by_patient_questionnaire(patient))
    elif type == 'form':
        return filter_by_patient_form(patient)
    else:
        return filter_by_patient_questionnaire(patient)


def filter_by_type(type):
    if type == 'form':
        return GroupForm.query.filter(GroupForm.form_id == Form.id).exists()
    else:
        return GroupQuestionnaire.query.filter(GroupQuestionnaire.form_id == Form.id).exists()


class FormListView(ListModelView):
    serializer_class = FormSerializer
    model_class = Form

    def filter_query(self, query):
        query = super(FormListView, self).filter_query(query)

        args = parse_args(FormListRequestSerializer)

        patient = args['patient']
        type = args['type']
        slug = args['slug']

        if slug is not None:
            # Filter by form slug
            query = query.filter(Form.slug == slug)
        elif patient is not None:
            # Filter by forms relevant to patient
            query = query.filter(filter_by_patient(patient, type))
        elif type is not None:
            # Filter by form type
            query = query.filter(filter_by_type(type))

        return query


class FormCountListView(ListView):
    serializer_class = FormCountSerializer

    def get_object_list(self):
        args = parse_args(FormCountListRequestSerializer)

        patient = args['patient']
        type = args['type']

        count_query = db.session.query(
            Entry.form_id.label('form_id'),
            func.count().label('entry_count')
        )
        count_query = count_query.select_from(Entry)

        if patient is not None:
            # Only include entries that belong to this patient
            count_query = count_query.filter(Entry.patient == patient)

        count_query = count_query.group_by(Entry.form_id)
        count_subquery = count_query.subquery()

        q = db.session.query(Form, func.coalesce(count_subquery.c.entry_count, 0))
        q = q.outerjoin(count_subquery, Form.id == count_subquery.c.form_id)

        if patient is not None:
            # Filter by forms relevant to patient
            q = q.filter(filter_by_patient(patient, type))
        elif type is not None:
            # Filter by form type
            q = q.filter(filter_by_type(type))

        q = q.order_by(Form.id)

        results = [dict(form=form, count=count) for form, count in q]

        return results


class FormDetailView(RetrieveModelView):
    serializer_class = FormSerializer
    model_class = Form


class EntryListView(PatientObjectListView):
    serializer_class = EntrySerializer
    model_class = Entry

    def filter_query(self, query):
        query = super(EntryListView, self).filter_query(query)

        args = parse_args(EntryRequestSerializer)

        form_id = args['form']

        # Filter by entries by form
        if form_id is not None:
            query = query.filter(Entry.form_id == form_id)

        return query


class EntryDetailView(PatientObjectDetailView):
    serializer_class = EntrySerializer
    model_class = Entry


def register_views(app):
    app.add_url_rule('/forms', view_func=FormListView.as_view('form_list'))
    app.add_url_rule('/forms/<id>', view_func=FormDetailView.as_view('form_detail'))
    app.add_url_rule('/entries', view_func=EntryListView.as_view('entry_list'))
    app.add_url_rule('/entries/<id>', view_func=EntryDetailView.as_view('entry_detail'))
    app.add_url_rule('/form-counts', view_func=FormCountListView.as_view('form_count_list'))
