import re
import cgi
import hashlib
import random


from string import letters

secret = "secretword"

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+\.[\S]+$")

def checkUsername(user):
	return USER_RE.match(user)

def checkPass(password):
	return PASS_RE.match(password)

def checkEmail(email):
	return not email or EMAIL_RE.match(email)

def comparePassword(password, verify):
	if(password == verify):
		return True
	return False

def escape(s):
	return cgi.escape(s, quote=True)
	
def make_salt(length = 5):
	return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s|%s' % (salt, h)

def valid_pw(name, password, h):
	salt = h.split('|')[0]
	return h == make_pw_hash(name, password, salt)
	

	
	