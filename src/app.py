from flask import Flask , request , make_response
from routes.auth import auth_bp
from routes.job import job_bp

app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(job_bp)
