from flask.ext.script import Manager, Server

# Import the main Flask app
from app import app

# Get Blueprint Apps
from jobs import jobs_app
from resume import resume_app
from auth import auth_login
from analytics import analytics_app

# Register Blueprints
app.register_blueprint(auth_login, url_prefix='/user')
app.register_blueprint(jobs_app, url_prefix='/jobs')
app.register_blueprint(resume_app, url_prefix='/resumes')
app.register_blueprint(analytics_app, url_prefix='/analytics')

manager = Manager(app)

port = 9000
manager.add_command("runserver", Server(host="0.0.0.0", port=port))

if __name__ == '__main__':
	#For testing
	#import os

	#open browser pointing at app
	#os.system("open http://localhost:{0}".format(port))

	manager.run()