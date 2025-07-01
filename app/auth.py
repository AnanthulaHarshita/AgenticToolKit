"""from flask import app, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

oauth = OAuth()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email

    def get_id(self):
        return self.id

# In-memory user store (for demo)
users = {}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Setup OAuth
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id='1011231083534-g40q77dtos2l6i1mvoqlbio2ll4brp6o.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token)
    user = User(
        id_=user_info['sub'],
        name=user_info['name'],
        email=user_info['email']
    )
    users[user.id] = user
    login_user(user)
    return redirect('/')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

# Protect your routes
@app.route("/content-generator", methods=["GET", "POST"])
@login_required
def content_generator():
    # ...existing code...
    pass
"""