import models
from flask.ext.login import UserMixin
from hashlib import md5


class User(UserMixin):
	def __init__(self, email=None, password=None, active=True, username=None, id=None):
		self.username = username
		self.email = email
		self.password = password
		self.active = active
		self.isAdmin = False
		self.id = None

	def save(self):
		newUser = models.User(email=self.email, password=self.password, active=self.active, username=self.username)
		newUser.save()
		print "new user id = %s " % newUser.id
		self.id = newUser.id
		return self.id

	def get_by_id(self, id):
		dbUser = models.User.objects.with_id(id)
		if dbUser:
			self.email = dbUser.email
			self.username = dbUser.username
			self.active = dbUser.active
			self.id = dbUser.id

			return self
		else:
			return None

	def reset_password(self, user_id, password):
		dbUser = models.User.objects.with_id(user_id)
		dbUser.password = password
		print "Trying to change password of user id = %s " % user_id
		dbUser.save()
		print "changed password of user id = %s " % user_id
		return self

	def get_by_email_w_password(self, email):

		try:
			dbUser = models.User.objects.get_or_404(email=email)
			
			if dbUser:
				self.email = dbUser.email
				self.username = dbUser.username
				self.active = dbUser.active
				self.password = dbUser.password
				self.id = dbUser.id
				
				return self
			else:
				return None
		except:
			print "error retrieving user"
			return None

	@classmethod
	def avatar(self, email, size):
		try:
			return 'http://www.gravatar.com/avatar/' + md5(email).hexdigest() + '?d=mm&s=' + str(size)
		except:
			return None

	def get_by_username(self, uname):

		try:
			dbUser = models.User.objects.get_or_404(username=uname)
			
			if dbUser:
				self.email = dbUser.email
				self.username = dbUser.username
				self.username = dbUser.username
				self.active = dbUser.active
				self.password = dbUser.password
				self.id = dbUser.id
				
				return self
			else:
				return None
		except:
			print "error retrieving user"
			return None
