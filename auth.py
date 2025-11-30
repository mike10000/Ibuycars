"""
Google OAuth Authentication Module
"""
import json
from flask import url_for, session, redirect, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import google.oauth2.credentials
import google_auth_oauthlib.flow
import requests
from config import config


class User(UserMixin):
    """User model for Flask-Login"""
    def __init__(self, id, name, email, picture):
        self.id = id
        self.name = name
        self.email = email
        self.picture = picture
        
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id


# Initialize Flask-Login
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    """Load user from session"""
    if 'user' in session:
        user_data = session['user']
        return User(
            id=user_data.get('id'),
            name=user_data.get('name'),
            email=user_data.get('email'),
            picture=user_data.get('picture')
        )
    return None


def init_oauth(app):
    """Initialize OAuth with Flask app"""
    login_manager.init_app(app)
    login_manager.login_view = 'login'


def get_google_provider_cfg():
    """Get Google's OAuth 2.0 configuration"""
    return requests.get(config.GOOGLE_DISCOVERY_URL).json()


def create_oauth_flow(redirect_uri=None):
    """Create OAuth flow"""
    google_provider_cfg = get_google_provider_cfg()
    
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": config.GOOGLE_CLIENT_ID,
                "client_secret": config.GOOGLE_CLIENT_SECRET,
                "auth_uri": google_provider_cfg["authorization_endpoint"],
                "token_uri": google_provider_cfg["token_endpoint"],
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
    )
    
    if redirect_uri:
        flow.redirect_uri = redirect_uri
    
    return flow


def validate_domain(email):
    """Check if email domain is allowed"""
    domain = email.split('@')[1] if '@' in email else ''
    return domain in config.ALLOWED_DOMAINS


def create_user_from_google_info(userinfo):
    """Create User object from Google userinfo"""
    return User(
        id=userinfo.get("sub"),
        name=userinfo.get("name"),
        email=userinfo.get("email"),
        picture=userinfo.get("picture")
    )
