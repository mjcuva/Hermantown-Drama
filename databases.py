import util
import datetime

from google.appengine.ext import db

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    permissions = db.StringProperty(default = "User", choices=set(["User", "Admin", "God"]))

    @classmethod
    def register(cls, name, password, email):
        pw_hash = util.make_pw_hash(email, password)
        return User(name = name, pw_hash = pw_hash, email = email, permissions = "User")

    @classmethod
    def by_name(cls, name):
        u = User.all().filter("name =", name).get()
        return u

    @classmethod
    def by_email(cls, email):
        u = User.all().filter("email =", email).get()
        return u

class Post(db.Model):
    author = db.ReferenceProperty(User)
    content = db.TextProperty(required = True)
    time = db.DateTimeProperty(auto_now_add = False)
    applause = db.IntegerProperty(default = 0)

    @classmethod
    def addPost(cls, author, content):
        time = datetime.datetime.now()
        post = Post(author = author, content = content, time = time)
        post.put()
        return post

class Comment(db.Model):
    post = db.ReferenceProperty(Post)
    content = db.TextProperty(required = True)
    author = db.ReferenceProperty(User)
    time = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def addComment(cls, post, author, content):
        comment = Comment(post = post, author = author, content = content)
        comment.put()
        return comment

class userImage(db.Model):
    name = db.StringProperty()
    data = db.BlobProperty()
    filetype = db.StringProperty()
    user = db.ReferenceProperty(User)

    @classmethod
    def by_user_id(cls, id):
        user = User.get_by_id(int(id))
        images = userImage.all()
        for i in images:
            if i.user.key().id() == user.key().id():
                return image

class largeImage(db.Model):
    url = db.StringProperty()
    thumbnail = db.BlobProperty()
    user = db.ReferenceProperty(User)
    caption = db.TextProperty()
    posted = db.DateTimeProperty(auto_now_add = True)

class applause(db.Model):
    post = db.ReferenceProperty(Post)
    user = db.ReferenceProperty(User)

class frontPage(db.Model):
    text = db.TextProperty()

    @classmethod
    def getText(cls):
        frontPage = cls.all()
        if(frontPage.count() > 0):
            frontPage = frontPage[0].text
        else:
            frontPage = ""

        return frontPage


class sidebar(db.Model):
    text = db.TextProperty()

    @classmethod
    def getText(cls):
        sidebar = cls.all()
        if(sidebar.count() > 0):
            sidebar = sidebar[0].text
        else:
            sidebar = ""

        return sidebar







