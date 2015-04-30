from flask import render_template, Blueprint, abort, request, url_for, redirect
from flask_login import current_user, login_required
from radar.database import db

from radar.patients.models import Patient, Demographics
from radar.ordering import Ordering
from radar.pagination import paginate_query
from radar.patients.core import view_patient_list_permission
from radar.patients.forms import PatientSearchForm, PER_PAGE_DEFAULT, PER_PAGE_CHOICES, DemographicsForm
from radar.patients.sda import demographics_to_sda_bundle
from radar.patients.search import PatientQueryBuilder
from radar.sda.models import SDAPatient
from radar.services import get_disease_group_filters_for_user, get_unit_filters_for_user


bp = Blueprint('patients', __name__)


def get_patient_data(patient):
    units = sorted(patient.filter_units_for_user(current_user), key=lambda x: x.unit.name)
    disease_groups = sorted(patient.filter_disease_groups_for_user(current_user), key=lambda x: x.disease_group.name)

    return dict(
        units=units,
        disease_groups=disease_groups,
    )


@bp.route('/')
def view_patient_list():
    if not view_patient_list_permission(current_user):
        abort(403)

    form = PatientSearchForm(formdata=request.args, csrf_enabled=False)

    disease_group_choices = [(x.id, x.name) for x in get_disease_group_filters_for_user(current_user)]
    disease_group_choices.insert(0, ('', ''))
    form.disease_group_id.choices = disease_group_choices

    unit_choices = [(x.id, x.name) for x in get_unit_filters_for_user(current_user)]
    unit_choices.insert(0, ('', ''))
    form.unit_id.choices = unit_choices

    builder = PatientQueryBuilder(current_user)

    if form.validate():
        if form.first_name.data:
            builder.first_name(form.first_name.data)

        if form.last_name.data:
            builder.last_name(form.last_name.data)

        if form.unit_id.data:
            builder.unit(form.unit_id.data)

        if form.disease_group_id.data:
            builder.disease_group(form.disease_group_id.data)

        if form.date_of_birth.data:
            builder.date_of_birth(form.date_of_birth.data)

        if form.patient_number.data:
            builder.patient_number(form.patient_number.data)

        if form.gender.data:
            builder.gender(form.gender.data)

        if form.radar_id.data:
            builder.radar_id(form.radar_id.data)

        if form.year_of_birth.data:
            builder.year_of_birth(form.year_of_birth.data)

        builder.order_by(form.order_by.data, form.order_direction.data)

    query = builder.build()

    ordering = Ordering(form.order_by.data, form.order_direction.data)
    pagination = paginate_query(query, default_per_page=PER_PAGE_DEFAULT)
    patients = pagination.items

    patients = [(x, get_patient_data(x)) for x in patients]

    context = dict(
        patients=patients,
        form=form,
        pagination=pagination,
        ordering=ordering,
        per_page_choices=PER_PAGE_CHOICES,
    )

    return render_template('patients.html', **context)

@login_required
@bp.route('/<int:patient_id>/', endpoint='view_demographics_list')
@bp.route('/<int:patient_id>/', endpoint='view_patient')
def view_demographics_list(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if not patient.can_view(current_user):
        abort(403)

    sda_patients = SDAPatient.query\
        .join(SDAPatient.sda_bundle)\
        .join(Patient)\
        .filter(Patient.id == patient_id)\
        .all()

    demographics_list = []

    for sda_patient in sda_patients:
        demographics = dict()

        demographics['facility'] = sda_patient.sda_bundle.facility
        demographics['first_name'] = sda_patient.first_name
        demographics['last_name'] = sda_patient.last_name
        demographics['date_of_birth'] = sda_patient.date_of_birth

        if sda_patient.gender == 'M':
            demographics['gender'] = 'Male'
        else:
            demographics['gender'] = 'Female'

        demographics['addresses'] = []
        addresses = sorted(sda_patient.addresses, key=lambda x: x.to_time)

        for address in addresses:
            demographics['addresses'].append({
                'from_time': address.from_time,
                'to_time': address.to_time,
                'address': address.full_address
            })

        demographics_list.append(demographics)

    context = dict(
        patient=patient,
        patient_data=get_patient_data(patient),
        demographics_list=demographics_list
    )

    return render_template('patient/demographics.html', **context)


@bp.route('/<int:patient_id>/radar/', endpoint='view_radar_demographics')
@bp.route('/<int:patient_id>/radar/', endpoint='edit_radar_demographics', methods=['POST'])
def view_radar_demographics(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    demographics = Demographics.query.filter(Demographics.patient == patient).with_for_update(read=True).first()

    if demographics is None:
        demographics = Demographics(patient=patient)

    if not demographics.can_view(current_user):
        abort(403)

    read_only = not demographics.can_edit(current_user)

    form = DemographicsForm(obj=demographics)

    if request.method == 'POST':
        if read_only:
            abort(403)

        if form.validate():
            form.populate_obj(demographics)

            sda_bundle = demographics_to_sda_bundle(demographics)
            sda_bundle.serialize()
            demographics.sda_bundle = sda_bundle

            db.session.add(demographics)
            db.session.commit()
            return redirect(url_for('patients.view_demographics_list', patient_id=demographics.patient.id))

    context = dict(
        patient=demographics.patient,
        patient_data=get_patient_data(demographics.patient),
        demographics=demographics,
        form=form,
        read_only=read_only
    )

    return render_template('patient/radar_demographics.html', **context)


@bp.route('/<int:patient_id>/disease-groups/')
def view_patient_disease_groups(patient_id):
    return render_template('patient/disease_groups.html')


@bp.route('/<int:patient_id>/units/')
def view_patient_units(patient_id):
    return render_template('patient/units.html')