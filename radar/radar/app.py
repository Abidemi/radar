from flask import Flask

from radar.database import db


def create_app():
    app = Flask(__name__)
    app.config.from_object('radar.default_settings')
    app.config.from_envvar('RADAR_SETTINGS')

    # noinspection PyUnresolvedReferences
    from radar import models  # noqa

    db.init_app(app)

    return app
