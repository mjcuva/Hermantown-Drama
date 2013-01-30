import webapp2
import jinja2
import os
import util
import databases
import hmac
import json
import logging
import urllib

from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images


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
        return self.response.headers.add_header("Set-Cookie", "%s=%s" % (name, val))

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
            content = util.htmlify(self.request.POST['content'])
            post = databases.Post.addPost(user, content)
            self.render("post.html", post = post, user = user)
            # output = {'name': user.name, 'content': self.request.get('content'), 'image': user.profileImage}
            # output = json.dumps(output)
            # self.write(output)


class addComment(Handler):
    def post(self):
        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
            content = util.htmlify(util.escape(self.request.POST['content']))
            logging.debug(content)
            postid = self.request.get('id')
            post = databases.Post.get_by_id(int(postid))
            if post:
                comment = databases.Comment.addComment(post, user, content)
                self.render('comments.html', comment = comment, post = post, user = user)       
            else:
                self.write('ERROR')

class applaud(Handler):
    def post(self):
        error = False
        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
            post = databases.Post.get_by_id(int(self.request.get('id')))
            for i in databases.applause.all():
                if i.post.key().id() == post.key().id() and i.user.key().id() == user.key().id():
                    self.write("ERROR")
                    error = True
            if not error:
                applaud = databases.applause(user = user, post = post)
                applaud.put()
                if post.applause:
                    post.applause += 1
                    post.put()
                    self.write(post.applause)
                else:
                    post.applause = 1
                    post.put()
                    self.write(post.applause)
        else:
            self.redirect('/')


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
            logging.info(u.name + " logged in")
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
            for applaud in databases.applause.all():
                if applaud.post.key().id() == post.key().id():
                    applaud.delete()
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
        firstname = user.name.split(' ')[0]
        lastname = user.name.split(' ')[1]

        if self.request.get('user_password') == '' or util.valid_pw(user.email, self.request.get('user_password'), user.pw_hash) == False:
            self.render('profile.html', password = 'Invalid Password', user = user, firstname = firstname, lastname = lastname)
        else:
            user.name = self.request.get('user_first') + " " + self.request.get('user_last')
            user.email = self.request.get('user_email')
            user.pw_hash = util.make_pw_hash(user.email, self.request.get('user_password'))
            user.put()

            if not self.request.POST[u'image'] == "":
                try:
                    data = self.request.POST[u'image'].file.read()
                    name = self.request.POST[u'image'].filename
                    filetype = self.request.POST[u'image'].type
                    image = databases.userImage(name = name, data = data, filetype = filetype, user = user)
                    for i in databases.userImage.all():
                        if i.user.key().id() == user.key().id():
                            logging.debug('Deleted: ' + i.name)
                            i.delete()

                    logging.debug("Put: " + image.name)
                    image.put()

                    self.redirect('/')
                except Exception as e:
                    error = "Image must be smaller than 1mb."
                    logging.error(e)
                    self.render('profile.html', user = user, firstname = firstname, lastname = lastname, error = error)
            else:
                logging.debug('No image')
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
        img = None
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

class uploadForm(Handler):
    def get(self):
        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
            upload_url = blobstore.create_upload_url("/upimage")
            self.render('upload.html', user = user, upload_url = upload_url)
        else:
            self.redirect('/')

class uploadImage(blobstore_handlers.BlobstoreUploadHandler):
    def thumbnailer(self, blob_key):
        blob_info = blobstore.get(blob_key)

        if blob_info:
            img = images.Image(blob_key=blob_key)
            img.resize(width=300, height=300)
            thumbnail = img.execute_transforms(output_encoding=images.PNG)
            return thumbnail

    def post(self):
        user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
        caption = self.request.get('caption')
        image = self.get_uploads('file')
        for i in image:
            blob_info = i
            image = databases.largeImage(url = '/image/%s' % blob_info.key(), user = user, caption = caption)
            image.put()

            thumbnail = self.thumbnailer(blob_info.key())
            image.thumbnail = thumbnail
            image.put()
        self.redirect('/photos/1')
    

class serve(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

class displayPhotos(Handler):

    def get(self, page):
        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))
        else:
            user = None
        imageCount = databases.largeImage.all().order('-posted').count()

        if(int(page) * 20 > imageCount):
            button = False
        else:
            button = True
        images = databases.largeImage.all().order('-posted')[:(20 * int(page))]
        self.render('images.html', images = images, user = user, button= button)

class displayThumbnail(Handler):

    def get(self, id):
        image = databases.largeImage.get_by_id(int(id)).thumbnail
        self.response.headers['Content-Type'] = 'image/png'
        self.write(image)


class editInfo(Handler):

    def get(self):

        if(self.request.cookies.get('user') and self.check_secure_val(self.request.cookies.get('user'))):
            user = databases.User.get_by_id(int(self.request.cookies.get('user').split('|')[0]))

        self.render('editinfo.html', user = user)
        




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
                                ('/changepassword', changePass),
                                ("/upload", uploadForm),
                                ('/upimage', uploadImage),
                                ('/image/([^/]+)?', serve),
                                ('/photos/(\d+)/?', displayPhotos),
                                ('/thumbnail/(\d+)', displayThumbnail),
                                ('/applaud', applaud),
                                ('/editinfo', editInfo)],
                              debug=True)
