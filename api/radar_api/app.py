import logging
from flask import Flask
from radar_api.auth import require_login

from radar_api.views import cohort_patients
from radar_api.views import consultants
from radar_api.views import forgot_password
from radar_api.views import organisation_consultants
from radar_api.views import patient_consultants
from radar_api.views import recruitment_stats
from radar_api.views import cohort_users
from radar_api.views import comorbidities
from radar_api.views import diagnoses
from radar_api.views import family_history
from radar_api.views import logout
from radar_api.views import organisation_patients
from radar_api.views import organisation_users
from radar_api.views import pathology
from radar_api.views import patient_addresses
from radar_api.views import patient_aliases
from radar_api.views import patient_demographics
from radar_api.views import dialysis
from radar_api.views import cohorts
from radar_api.views import data_sources
from radar_api.views import genetics
from radar_api.views import hospitalisations
from radar_api.views import medications
from radar_api.views import patient_numbers
from radar_api.views import patients
from radar_api.views import plasmapheresis
from radar_api.views import posts
from radar_api.views import renal_imaging
from radar_api.views import results
from radar_api.views import salt_wasting_clinical_features
from radar_api.views import organisations
from radar_api.views import user_sessions
from radar_api.views import transplants
from radar_api.views import users
from radar_api.views import login
from radar_api.views import forgot_username
from radar_api.views import reset_password
from radar.auth.cors import set_cors_headers
from radar.auth.sessions import refresh_token
from radar.database import db
from radar.template_filters import register_template_filters


class RadarApi(Flask):
    def __init__(self):
        super(RadarApi, self).__init__(__name__)

        self.public_endpoints = []

        self.config.from_object('radar.default_settings')
        self.config.from_object('radar_api.default_settings')
        self.config.from_envvar('RADAR_SETTINGS')

        db.init_app(self)

        if self.debug:
            self.after_request(set_cors_headers)

        if not self.debug:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            self.logger.addHandler(stream_handler)

        self.before_request(require_login)
        self.after_request(refresh_token)

        register_template_filters(self)

        cohorts.register_views(self)
        cohort_patients.register_views(self)
        cohort_users.register_views(self)
        comorbidities.register_views(self)
        consultants.register_views(self)
        data_sources.register_views(self)
        diagnoses.register_views(self)
        dialysis.register_views(self)
        family_history.register_views(self)
        forgot_password.register_views(self)
        forgot_username.register_views(self)
        genetics.register_views(self)
        hospitalisations.register_views(self)
        login.register_views(self)
        logout.register_views(self)
        medications.register_views(self)
        organisations.register_views(self)
        organisation_consultants.register_views(self)
        organisation_patients.register_views(self)
        organisation_users.register_views(self)
        pathology.register_views(self)
        patient_addresses.register_views(self)
        patient_aliases.register_views(self)
        patient_consultants.register_views(self)
        patient_demographics.register_views(self)
        patient_numbers.register_views(self)
        patients.register_views(self)
        plasmapheresis.register_views(self)
        posts.register_views(self)
        recruitment_stats.register_views(self)
        renal_imaging.register_views(self)
        reset_password.register_views(self)
        results.register_views(self)
        salt_wasting_clinical_features.register_views(self)
        transplants.register_views(self)
        users.register_views(self)
        user_sessions.register_views(self)

    def add_public_endpoint(self, endpoint):
        self.public_endpoints.append(endpoint)

    def is_public_endpoint(self, endpoint):
        return endpoint in self.public_endpoints


def create_app():
    return RadarApi()
