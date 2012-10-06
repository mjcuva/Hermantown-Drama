import webapp2
import jinja2
import os
import util
import databases
import hmac
import json
import logging

from google.appengine.ext import db
from google.appengine.api import urlfetch


secret = 'secret'

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))


# Shortcut handler for simpler function calls
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_cookie(self, name, value):
        val = self.make_secure_val(value)
        logging.error(val)
        return self.response.headers.add_header("Set-Cookie", "%s=%s; Path='/'" % (name, val))

    def make_secure_val(self, val):
        return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

    def check_secure_val(self, secure_val):
        val = secure_val.split('|')[0]
        if secure_val == self.make_secure_val(val):
            return val


class MainHandler(Handler):
    def get(self):
        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
        else:
            user = None
        posts = databases.Post.all().order('-time')
        comments = databases.Comment.all().order('time')

        images = databases.userImage.all()
        self.render('base.html', user = user, posts = posts, comments = comments, images = images)

    def post(self):
        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
            databases.Post.addPost(user, self.request.get("content"))
            output = {'test': test}
            output = json.dumps(output)
            self.write(output)


class addPost(Handler):
    def post(self):
        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
            content = self.request.get('content').replace('\n', '<br>')
            post = databases.Post.addPost(user, content)
            self.render("post.html", post = post, user = user)
            # output = {'name': user.name, 'content': self.request.get('content'), 'image': user.profileImage}
            # output = json.dumps(output)
            # self.write(output)


class addComment(Handler):
    def post(self):
        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
            content = self.request.get('content').replace('\n', '<br>')
            postid = self.request.get('id')
            post = databases.Post.get_by_id(int(postid))
            comment = databases.Comment.addComment(post, user, content)

            self.render('comments.html', comment = comment, post = post, user = user)       


class register(Handler):
    def get(self):
        self.render('signup.html')

    def post(self):
        name = util.escape(self.request.get("user_first") + " " + self.request.get("user_last"))
        password = util.escape(self.request.get("user_pass"))
        email = util.escape(self.request.get("user_email"))

        user = databases.User.register(name, password, email)

        user.put()

        data = db.Blob(urlfetch.Fetch("http://i.imgur.com/efHNR.gif").content)
        filetype = 'gif'
        name = 'blank_profile.gif'

        image = databases.userImage(name = name, data = data, filetype = filetype, user = user)
        image.put()

        self.set_cookie("user", str(user.key().id()))

        self.redirect('/')


class login(Handler):
    def get(self):
        self.render('login.html')

    def post(self):
        params = {}
        error = False

        email = util.escape(self.request.get("email"))
        password = util.escape(self.request.get("password"))
        
        params['email'] = email

        if not email:
            params['errorEmail'] = 'error'
            params['errorMessage'] = "Please enter email"
            error = True

        if not password:
            params['errorPass'] = 'error'
            params['errorMessage'] = "Please enter password"
            error = True

        u = databases.User.by_email(email)

        if not u:
            params['errorEmail'] = 'error'
            params['errorPass'] = 'error'
            params['errorMessage'] = "Invalid email"
            error = True
        elif not util.valid_pw(email, password, u.pw_hash):
            params['errorEmail'] = 'error'
            params['errorPass'] = 'error'
            params['errorMessage'] = "Invalid password"
            error = True

        if error:
            self.render('login.html', **params)
        else:
            self.set_cookie('user', str(u.key().id()))
            logging.error(self.request.cookies.get('user'))
            self.redirect('/')


class logout(Handler):
    def get(self):
        self.set_cookie('user', '')
        self.redirect('/')


class delete(Handler):
    def get(self):

        itemid = self.request.get("id")
        type = self.request.get('type')

        post = databases.Post.get_by_id(int(itemid))
        comment = databases.Comment.get_by_id(int(itemid))

        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
        else:
            self.redirect('/')

        if(type == 'post'):
            comments = databases.Comment.all()
            for comment in comments:
                if comment.post.key().id() == post.key().id():
                    comment.delete()
            post.delete()
        if(type == 'comment'):
            comment.delete()


class profile(Handler):
    def get(self):

        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
            firstname = user.name.split(' ')[0]
            lastname = user.name.split(' ')[1]
            self.render('profile.html', user = user, firstname = firstname, lastname = lastname)
        else:
            self.redirect('/')

    def post(self):
        user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))

        user.name = self.request.get('user_first') + " " + self.request.get('user_last')
        user.email = self.request.get('user_email')
        user.pw_hash = util.make_pw_hash(user.email, self.request.get('user_password'))
        user.put()

        if not self.request.POST[u'image'] == "":
            try:
                data = self.request.POST[u'image'].file.read()
                name = self.request.POST[u'image'].filename
                filetype = 'image/' + self.request.POST[u'image'].type
                image = databases.userImage(name = name, data = data, filetype = filetype, user = user)
                for i in databases.userImage.all():
                    if i.user.key().id() == user.key().id():
                        i.delete()
                image.put()

                self.redirect('/')
            except:
                error = "Image must be smaller than 1mb."
                firstname = user.name.split(' ')[0]
                lastname = user.name.split(' ')[1]
                self.render('profile.html', user = user, firstname = firstname, lastname = lastname, error = error)

        self.redirect('/')


class changePass(Handler):

    def get(self):
            if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
                user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
                self.render('changepass.html')
            else:
                self.redirect('/')

    def post(self):
        params = {}
        error = False
        if not self.request.get('oldpass'):
            params['oldpass'] = 'Please enter your current password'
            error = True

        if not self.request.get('newpass'):
            params['newpass'] = "Please enter a new password"
            error = True

        if not self.request.get('passval'):
            params['valpass'] = 'Please enter the new password again'
            error = True


        if not self.request.get('valpass') == self.request.get('newpass'):
            params['errorMessage'] = "Passwords didn't match"
        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
            oldpass = self.request.get('oldpass')
            newpass = self.request.get('newpass')
            passval = self.request.get('passval')

            if error:
                self.render("changepass.html", **params)
            else:
                if util.valid_pw(user.email, oldpass, user.pw_hash) and (newpass == newpass):
                    passhash = util.make_pw_hash(user.email, newpass)
                    user.pw_hash = passhash
                    user.put()
        
        self.redirect('/')



class imageHandler(Handler):
    def get(self, id):

        user = databases.User.get_by_id(int(id))
        images = databases.userImage.all()
        for i in images:
            try:
                if i.user.key().id() == user.key().id():
                    img = i
            except:
                pass

        if img:
            self.response.headers['Content-Type'] = 'text'
            self.response.out.write( img.data )




app = webapp2.WSGIApplication([('/', MainHandler),
                                ('/register/?', register),
                                ('/login/?', login),
                                ('/logout/?', logout),
                                ('/delete', delete),
                                ('/profile/(\d+)', profile),
                                ('/profile/?', profile),
                                ('/post$', addPost),
                                ('/addcomment$', addComment),
                                ('/img/(\d+)', imageHandler),
                                ('/changepassword', changePass)],
                              debug=True)
