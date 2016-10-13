from flask_admin import Admin

from radar.admin.views import (
    AdminIndexView,
    CodeView,
    ConsultantView,
    DiagnosisView,
    DiagnosisCodeView,
    DrugGroupView,
    DrugView,
    FormView,
    GroupView,
    GroupConsultantView,
    GroupDiagnosisView,
    GroupFormView,
    GroupObservationView,
    GroupQuestionnaireView,
    GroupPageView,
    ObservationView,
    SpecialtyView
)
from radar.app import Radar
from radar.auth.sessions import current_user
from radar.database import db
from radar.models.codes import Code
from radar.models.consultants import Consultant, Specialty, GroupConsultant
from radar.models.diagnoses import Diagnosis, GroupDiagnosis, DiagnosisCode
from radar.models.forms import Form, GroupForm, GroupQuestionnaire
from radar.models.groups import Group, GroupPage
from radar.models.medications import Drug, DrugGroup
from radar.models.results import Observation, GroupObservation


def inject_current_user():
    return dict(current_user=current_user)


class RadarAdmin(Radar):
    def __init__(self):
        super(RadarAdmin, self).__init__(template_folder='admin/templates')

        self.context_processor(inject_current_user)

        admin = Admin(self, 'RADAR Admin', index_view=AdminIndexView(), template_mode='bootstrap3', base_template='master.html', url='/admin')

        admin.add_view(GroupView(Group, db.session, name='Groups', category='Groups'))
        admin.add_view(GroupConsultantView(GroupConsultant, db.session, name='Consultants', category='Groups'))
        admin.add_view(GroupDiagnosisView(GroupDiagnosis, db.session, name='Diagnoses', category='Groups'))
        admin.add_view(GroupFormView(GroupForm, db.session, name='Forms', category='Groups'))
        admin.add_view(GroupObservationView(GroupObservation, db.session, name='Observations', category='Groups'))
        admin.add_view(GroupPageView(GroupPage, db.session, name='Pages', category='Groups'))
        admin.add_view(GroupQuestionnaireView(GroupQuestionnaire, db.session, name='Questionnaires', category='Groups'))

        admin.add_view(CodeView(Code, db.session, name='Codes'))

        admin.add_view(ConsultantView(Consultant, db.session, name='Consultants', category='Consultants'))
        admin.add_view(SpecialtyView(Specialty, db.session, 'Specialties', category='Consultants'))

        admin.add_view(DiagnosisView(Diagnosis, db.session, name='Diagnoses', category='Diagnoses'))
        admin.add_view(DiagnosisCodeView(DiagnosisCode, db.session, name='Codes', category='Diagnoses'))

        admin.add_view(DrugView(Drug, db.session, 'Drugs', category='Drugs'))
        admin.add_view(DrugGroupView(DrugGroup, db.session, 'Groups', category='Drugs'))

        admin.add_view(FormView(Form, db.session, 'Forms'))

        admin.add_view(ObservationView(Observation, db.session, 'Observations'))
