from flask import Flask, jsonify
from flask_cors import CORS

from actions.auth.login import login
from actions.auth.signup import signUp
from actions.auth.exit import exit
from actions.meeting.create_meeting import create_meeting
from actions.meeting.list_meeting import list_meeting
from actions.meeting.join_meeting import join_meeting
from actions.meeting.my_meetings import my_meetings
from actions.meeting.leave_meeting import leave_meeting
from actions.meeting.cancel_meeting import cancel_meeting
from actions.meeting.finish_meeting import finish_meeting
from actions.profile.update_profile import update_profile
from actions.profile.get_profile import get_profile
from actions.profile.sns_management import sns_management
from actions.admin.meetings import admin_meetings
from actions.admin.cancel_meeting import admin_cancel_meeting
from actions.admin.finish_meeting import admin_finish_meeting
from actions.admin.remove_user import admin_remove_user
from actions.admin.users import admin_users
from actions.admin.chat_partners import admin_chat_partners
from actions.admin.chat_history import admin_chat_history
from actions.admin.meeting_chat import admin_meeting_chat
from actions.chat.meeting_chat import meeting_chat
from actions.chat.private_chat import private_chat
from actions.chat.search_user import chat_search

app = Flask(__name__)
#CORS(app, resources={r"*": {"origins": "*"}}) 
#CORS(app)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})
     
app.register_blueprint(login, url_prefix='/api')
app.register_blueprint(signUp, url_prefix='/api')
app.register_blueprint(exit, url_prefix='/api')
app.register_blueprint(create_meeting, url_prefix='/api')
app.register_blueprint(list_meeting, url_prefix='/api')
app.register_blueprint(join_meeting, url_prefix='/api')
app.register_blueprint(my_meetings, url_prefix='/api')
app.register_blueprint(leave_meeting, url_prefix='/api')
app.register_blueprint(cancel_meeting, url_prefix='/api')
app.register_blueprint(finish_meeting, url_prefix='/api')
app.register_blueprint(update_profile, url_prefix='/api')
app.register_blueprint(get_profile, url_prefix='/api')
app.register_blueprint(sns_management, url_prefix='/api')
app.register_blueprint(admin_meetings, url_prefix='/api')
app.register_blueprint(admin_cancel_meeting, url_prefix='/api')
app.register_blueprint(admin_finish_meeting, url_prefix='/api')
app.register_blueprint(admin_remove_user, url_prefix='/api')
app.register_blueprint(admin_users, url_prefix='/api')
app.register_blueprint(admin_chat_partners, url_prefix='/api')
app.register_blueprint(admin_chat_history, url_prefix='/api')
app.register_blueprint(admin_meeting_chat, url_prefix='/api')
app.register_blueprint(meeting_chat, url_prefix='/api')
app.register_blueprint(private_chat, url_prefix='/api')
app.register_blueprint(chat_search, url_prefix='/api')