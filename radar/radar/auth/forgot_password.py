import base64
import os
from datetime import datetime

from flask import current_app

from radar.auth.exceptions import UserNotFound, InvalidToken
from radar.auth.passwords import generate_password_hash, check_password_hash
from radar.auth.sessions import logout_user
from radar.database import db
from radar.models import User
from radar.mail import send_email_from_template

RESET_PASSWORD_MAX_AGE = 86400  # 1 day


def generate_reset_password_token():
    # Token is given to user, hash is stored
    token = base64.urlsafe_b64encode(os.urandom(32))
    token_hash = generate_password_hash(token)
    return token, token_hash


def forgot_password(username):
    user = User.query.filter(User.username == username).first()

    if user is None:
        raise UserNotFound()

    token, token_hash = generate_reset_password_token()

    user.reset_password_token = token_hash
    user.reset_password_date = datetime.now()

    db.session.commit()

    reset_password_url = current_app.config['BASE_URL'] + '/reset-password/%s' % token

    send_email_from_template(user.email, 'RaDaR Password Reset', 'reset_password', {
        'reset_password_url': reset_password_url,
        'user': user,
    })


def reset_password(token, username, password):
    user = User.query.filter(User.username == username).first()

    # User not found
    if user is None:
        raise UserNotFound()

    # User hasn't reset their password
    if user.reset_password_token is None:
        raise InvalidToken()

    # Token doesn't match
    if not check_password_hash(user.reset_password_token, token):
        raise InvalidToken()

    # Token has expired
    if user.reset_password_date is not None and (user.reset_password_date - datetime.now()).seconds > RESET_PASSWORD_MAX_AGE:
        raise InvalidToken()

    # Update the user's password
    user.password = password

    # Logout all of the user's sessions
    logout_user(user)

    # Clear the reset password token
    user.reset_password_token = None
    user.reset_password_date = None

    db.session.commit()
