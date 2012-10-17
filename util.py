import re
import cgi
import hashlib
import random
import logging

import os

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

def htmlify(content):
	# Add Break
	content = content.replace('\n', '<br>')

	www = content.find('www')
	while www > -1:
		if not (content.find("http://") + 7 == (www)):
			content = content[:www] + 'http://' + content[www:]
		
		www = content.find('www', www + 10)


	# Add links
	link = content.find('http://')
	while link > -1:
		endlink = content.find(' ', link) + 1
		if endlink == 0: endlink = len(content)
		content = content[:link] + '<a href="' + content[link:endlink] + '">' + content[link + 7:endlink] + '</a>' + content[endlink:]
		link = content.find('http://', endlink)


	# Add Markdown italics, bold, bold/italics
	while content.find('***') > -1:
		start = content.find('***')
		end = content.find('***', start + 1) + 1
		if end == 0: end = len(content)
		content = content[:start] + '<strong><em>' + content[start + 3:end - 1] + '</em></strong>' + content[end + 2:]
		start = content.find('***', end)

	while content.find('**') > -1:
		start = content.find('**')
		end = content.find('**', start + 1) + 1
		if end == 0: end = len(content)
		content = content[:start] + '<strong>' + content[start + 2 : end - 1] + '</strong>' + content[end + 1:]
		start = content.find('**', end)

	while content.find("*") > -1:
		start = content.find('*')
		end = content.find('*', start + 1) + 1
		if end == 0: end = len(content)
		content = content[:start] + '<em>' + content[start + 1:end - 1] + '</em>' + content[end:]
		start = content.find('*', end)

	# GIF ME
	if content.lower() == '#gif me':
		image = random.randint(1, 28)
		content = "<img src='/gifs/" + str(image) + ".gif'>"

	return content
	

	
	