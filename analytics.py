from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify, make_response
from flask.views import MethodView
from flask.ext.login import login_required
from models import User
import json

analytics_app = Blueprint('analytics_app', __name__, template_folder='templates', static_folder='static', static_url_path='/static')

class AnalyticsView(MethodView):
	decorators = [login_required]

	def get(self):
		#Get reference of current user and send it to template
		#Should only send relevant stats based on user
		curr_user = User.objects.get_or_404(email=g.user.email)
		return render_template('analytics/dash.html', user=curr_user)


analytics_app.add_url_rule('/', view_func=AnalyticsView.as_view('analytics'), methods=['GET'])

