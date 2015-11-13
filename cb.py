# all the imports
import sqlite3
import datetime
import os
import ast
import pandas as pd
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash,jsonify, send_file

from flask_table import Table, Col, LinkCol,ButtonCol
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user, AnonymousUserMixin
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField,HiddenField, TextField,PasswordField,validators,SelectField,RadioField,IntegerField,DecimalField,TextAreaField
from wtforms.validators import DataRequired, URL, Email
from flask.ext.bcrypt import Bcrypt
from contextlib import closing
from flask.ext.mail import Mail, Message
from flask_bootstrap import Bootstrap
from flask_oauthlib.client import OAuth
from flaskext.uploads import UploadSet, IMAGES, configure_uploads,UploadNotAllowed
import numpy as np
import json
from flask_sslify import SSLify
from time import sleep
from itsdangerous import URLSafeTimedSerializer
# from pyzipcode import ZipCodeDatabase
import random
import sys
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSON, JSONB
from Crypto.Cipher import DES


def make8(toEncrypt):
    lenToEncrypt = len(toEncrypt)
    wholeLen8 = lenToEncrypt/8
    wholeLen8b = (wholeLen8+1)*8
    thisManyMoreNeeded = wholeLen8b - lenToEncrypt
    ls = ['x' for x in xrange(thisManyMoreNeeded)]
    more = ''.join(ls)
    toEncrypt = toEncrypt + more
    return toEncrypt, thisManyMoreNeeded

def getMatches(myId):
    sql = 'SELECT * FROM multi WHERE "uId" = %(myId)s'
    myDF = pd.read_sql(sql, db.engine, params={'myId':myId})
    myEmails = myDF[myDF.me==1].ciph.tolist()
    peopleIListed = myDF[myDF.me==0].ciph.tolist()
    sql = 'SELECT * FROM multi WHERE me = 1 and "ciph" in %(ciphs)s'
    hitsOnMyList = pd.read_sql(sql, db.engine, params={'ciphs':tuple(peopleIListed)})
    if len(hitsOnMyList) > 0:
        hitsOnMyListIds = hitsOnMyList.uId
        sql = 'SELECT * FROM multi WHERE me = 0 and "uId" in %(hitsOnMyListIds)s'
        whatTheyListed = pd.read_sql(sql, db.engine, params={'hitsOnMyListIds':tuple(hitsOnMyListIds)})
        whatTheyListed = whatTheyListed[whatTheyListed.ciph.isin(myEmails)]
        sendEmailsThemIds = whatTheyListed.uId.unique().tolist()
        sendEmailsThem = hitsOnMyList[hitsOnMyList.uId.isin(sendEmailsThemIds)][['origLen','ciph']].to_dict(orient='records')
        sendEmailsMe = whatTheyListed[['origLen','ciph']].to_dict(orient='records')
        obj = DES.new(EMAIL_KEY, DES.MODE_ECB)
        sendEmailsThem2=[]
        for ciphd in sendEmailsThem:
            ciphd2 = ciphd['ciph']
            ciphd2 = ciphd2.encode('Latin-1')
            decryptd = obj.decrypt(ciphd2)
            origLen = ciphd['origLen']
            decryptd = decryptd[:origLen]
            sendEmailsThem2.append(decryptd)
        sendEmailsMe2=[]
        for ciphd in sendEmailsMe:
            ciphd2 = ciphd['ciph']
            ciphd2 = ciphd2.encode('Latin-1')
            decryptd = obj.decrypt(ciphd2)
            origLen = ciphd['origLen']
            decryptd = decryptd[:origLen]
            sendEmailsMe2.append(decryptd)
        return sendEmailsMe2, sendEmailsThem2
    else:
        return None,None
# def sendMatchEmail(you,SO):
#     subj = 'message from CleanBreak'
#     msg = Message(subj,sender='info@cleanbreak.co',recipients=[you]) #this becomes you
#     h1 = "<p> the person below independently confirmed your request to break-up. thank you for using CleanBreak.</p><br>"
#     h2 = "<br><br><a href='"
#     h3 = "'>tell your story here</a>"
#     msg.html = h1 + SO + h2 + url_for('stories',_external=True) + h3
#     mail.send(msg)
#     return 'success'

def sendEmail(recipient,msgType, SO='you forgot to add one'):
    sender = DEFAULT_EMAIL_SENDER
    # subj = 'message from CleanBreak'
    if msgType == 'match':
        subject = 'message from CleanBreak'
        msg = Message(subject,sender=sender,recipients=[recipient]) #this becomes you
        h1 = "<p> the person below independently confirmed your request to break-up. thank you for using CleanBreak.</p><br>"
        h2 = "<br><br><a href='"
        h3 = "'>tell your story here</a>"
        msg.html = h1 + SO + h2 + url_for('stories',_external=True) + h3
    elif msgType == 'add':
        subject = 'confirm your email'
        token = ts.dumps(recipient, salt=EMAIL_CONFIRM_KEY)
        confirm_url = url_for(
            'confirm_email',
            token=token,
            _external=True)
        msg = Message(subject,sender=sender,recipients=[recipient])
        h1 = "<p> please click the link below to confirm your email address </p> <a href='"
        h2 = "'>click it</a>"
        h3 = h1 + confirm_url + h2
        msg.html = h3
    try:
        mail.send(msg)
    except Exception as e:
        print 'print e', e
        try:
            e2 = e.__dict__
            e3 = e2['recipients'].values()[0]
            code = e2['recipients'].values()[0][0]
            if code == 504:
                return 'badSOEmail'
        except:
            pass
    except:
        e = sys.exc_info()[0]
        print 'round two ', e
    return 'success'



# configuration
DEBUG = True
SECRET_KEY = 'WbKJyaTPCaMBEsOub0EDLaeNoTblNSinLDGaI8ky6PXvPyqdGw'
EMAIL_KEY = 'WcCkh7lh'
EMAIL_CONFIRM_KEY = 'eVFz77dDyfhEXjgElogylDm7w'
UPLOADS_DEFAULT_DEST = 'uploads'
BCRYPT_LOG_ROUNDS = 12
DEFAULT_EMAIL_SENDER = 'info@cleanbreak.co'
# if '/usr/local/bin' in sys.path:
# SQLALCHEMY_DATABASE_URI = "postgresql://super:mr084211@mritchie712-66.postgres.pythonanywhere-services.com:10066/cb"
# else:
SQLALCHEMY_DATABASE_URI = "postgresql://mritchie712:Mr084211@localhost/bu"

# pyAny
# UPLOADS_DEFAULT_DEST = 'gather/uploads'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
bootstrap = Bootstrap(app)
sslify = SSLify(app)
mail=Mail(app)
oauth = OAuth(app)
bcrypt = Bcrypt(app)

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# app.config.update(
#     #EMAIL SETTINGS
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT=465,
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME = 'mritchie712@gmail.com',
#     MAIL_PASSWORD = 'mjr084211',
#     SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI
#     )


app.config.update(
    #EMAIL SETTINGS
    MAIL_SERVER='mail.privateemail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = 'info@cleanbreak.co',
    MAIL_PASSWORD = 'mr084211',
    SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI
    )




mail=Mail(app)

app.config['UPLOADED_CSVFILES_DEST'] = '/var/uploads'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, (photos,))


# Facebook app details
FB_APP_ID = '475331005966645'
FB_APP_NAME = 'gatherDev'
FB_APP_SECRET = '1e36ff18c6e21d2d9a2de23ddfddcf78'


db = SQLAlchemy(app)


class AppUsers(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True)
    _password = db.Column(db.String(128))
    dt = db.Column(db.DateTime())
    crypEmail = db.Column(db.String())
    uData = db.Column(JSONB)
    email_confirmed = db.Column(db.Integer, default=0)

    def __init__(self, username,password, crypEmail, dt, uData):
        self.username = username
        self.password = password
        self.crypEmail = crypEmail
        self.dt = dt
        self.uData = uData

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    def is_authenticated(self):
        return True
    def is_anonymous(self):
        return False
        #return true if annon, actual user return false
    def is_active(self):
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.username
        #return unicode id for user, and used to load user from user_loader callback
    def get_id_int(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        # cur = g.db.execute('SELECT id from users where email=?',[self.email])
        # q = db.session.query(AppUsers).filter_by(username = self.username).first()
        q = AppUsers.query.filter_by(username = self.username).first()
        d = q.id
        return d

    def __repr__(self):
        return '<User %r>' % (self.username)


class Multi(db.Model):
    __tablename__ = "multi"
    id = db.Column(db.Integer, primary_key=True)
    uId = db.Column(db.Integer())
    dt = db.Column(db.DateTime())
    ciph = db.Column(db.String())
    origLen = db.Column(db.Integer())
    me = db.Column(db.Integer())

    def __init__(self, uId,dt,origLen,ciph, me):
        self.uId = uId
        self.dt = dt
        self.ciph = ciph
        self.origLen = origLen
        self.me = me

class Faqs(db.Model):
    __tablename__ = "faqs"
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(JSONB)

    def __init__(self, details):
        self.details = details

class Stories(db.Model):
    __tablename__ = "stories"
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(JSONB)
    dt = db.Column(db.DateTime())
    username = db.Column(db.String())

    def __init__(self, details, dt, username):
        self.details = details
        self.dt = dt
        self.username = username


class Votes(db.Model):
    __tablename__ = "votes"
    id = db.Column(db.Integer, primary_key=True)
    sId = db.Column(db.Integer)
    dt = db.Column(db.DateTime())
    username = db.Column(db.String())
    vote = db.Column(db.Integer)

    def __init__(self, sId, vote, dt, username):
        self.sId = sId
        self.vote = vote
        self.dt = dt
        self.username = username

login_manager = LoginManager()
login_manager.init_app(app)


class User():

    def __init__(self,username,password, active = True):
        self.username = username
        self.set_password(password)
        self.active = active

    def is_authenticated(self):
        return True
        #return true if user is authenticated, provided credentials

    def is_active(self):
        return True
    #return true if user is activte and authenticated

    def is_anonymous(self):
        return False
        #return true if annon, actual user return false

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.username
        #return unicode id for user, and used to load user from user_loader callback
    def get_id_int(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        # cur = g.db.execute('SELECT id from users where email=?',[self.email])
        # q = db.session.query(AppUsers).filter_by(username = self.username).first()
        q = AppUsers.query.filter_by(username = self.username).first()
        d = q.id
        return d


    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def __repr__(self):
        return '<User %r>' % (self.username)

class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = None

login_manager.anonymous_user = Anonymous

@login_manager.user_loader
def load_user(username):
    return AppUsers.query.filter_by(username=username).first()

@app.route('/')
# @login_required
def index():
    # cur2 = g.db.execute('SELECT community, count(1) as members from users group by community')
    # comCt = [dict(community=row[0], members=row[1]) for row in cur2.fetchall()]
    # email = None
    # if current_user.email:
        # email = current_user.email
    return render_template('about.html', current_user=current_user.username)

@app.route('/about')
# @login_required
def about():
    return render_template('about.html', current_user=current_user.username)

@app.route('/faq')
# @login_required
def faq():
    return render_template('faq.html')

@app.route('/stories')
# @login_required
def stories():
    return render_template('stories.html', current_user=current_user.username)

@app.route('/get_my_ip', methods=["GET"])
def get_my_ip():
    # return jsonify({'ip': request.remote_addr}), 200
    # return jsonify({'ip': request.environ['REMOTE_ADDR']}), 200
    return jsonify({'ip': str(request.headers)}), 200
    headers




############################################### animated form ##############################################################
##############################################################################################################################


@app.route('/form_index', methods=['GET','POST'])
def form_index():
    return render_template('form_index.html', app_id=FB_APP_ID)


@app.route('/<path:template>.html')
def route_templates(template):
    template_file = '{}.html'.format(template)
    return send_file(os.path.join(app.root_path,'templates',template_file))


@app.route('/search_faq')
def search_faq():
    faqLs=[]
    faqs = db.session.query(Faqs).all()
    for faq in faqs:
        faq.details = str(faq.details)
        details2 = ast.literal_eval(faq.details)
        faqLs.append(details2)
    return json.dumps(faqLs)

@app.route('/search_stories')
def search_stories():
    faqLs=[]
    faqs = db.session.query(Stories).all()
    for faq in faqs:
        faq.details = str(faq.details)
        details2 = ast.literal_eval(faq.details)
        details2['id'] = faq.id
        story = details2['story']
        maxLen=30
        if len(story) > maxLen:
            details2['title'] = story[:maxLen] + '...'
        faqLs.append(details2)
    print faqLs
    return json.dumps(faqLs)

@app.route('/get_user')
def get_user():
    return jsonify(username = current_user.username)
    # return 'asfasdf'

###############################################  login / logout   ############################################################
##############################################################################################################################



@app.route('/login', methods=["GET", "POST"])
def login():
    return render_template("login.html", current_user=current_user.username)

@app.route('/login_req',methods=['GET','POST'])
def login_req():
    uData = request.get_json()
    username = uData['username']
    password = uData['pass']
    user = AppUsers.query.filter_by(username=username).first()
    if not user:
        return '{ "loginStatus" : -1 }'
    elif user.is_correct_password(password):
        login_user(user)
    else:
        return '{ "loginStatus" : -1 }'
    return '{ "loginStatus" : 1 }'

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    try:
        session.clear()
    except:
        pass
    logout_user()
    return redirect(url_for('index'))


@app.route('/confirm_email/<token>', methods=["GET", "POST"])
def confirm_email(token):
    email = ts.loads(token, salt=EMAIL_CONFIRM_KEY, max_age=86400)
    email2, emailXs=make8(email)
    obj = DES.new(EMAIL_KEY, DES.MODE_ECB)
    ciph = obj.encrypt(email2)
    ciph = ciph.decode('Latin-1')
    user = AppUsers.query.filter_by(crypEmail=ciph).first()
    user.email_confirmed = 1
    uId = user.id
    # print email, email2, ciph, uId
    db.session.add(user)
    db.session.commit()
    you, SO = getMatches(uId)
    if SO:
        SO = SO[0]
        you = you[0]
        res1 = sendEmail(you,'match', SO=SO)
        res2 = sendEmail(SO,'match', SO=you)
        if res1 == 'badSOEmail':
            session['badSOEmail'] = True
        elif res2 == 'badSOEmail':
            session['badSOEmail'] = True
        else:
            session['badSOEmail'] = None

    return redirect(url_for('profile'))


@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    username = current_user.username
    email_confirmed = current_user.email_confirmed
    user = AppUsers.query.filter_by(username=username).first()
    dt = user.dt
    # dt = dt.isoformat()
    dt = dt.strftime("%D")
    try:
        badSOEmail = session['badSOEmail']
    except:
        badSOEmail = None
    return render_template("profile.html", username=username, dt=dt, email_confirmed=email_confirmed, current_user=current_user.username, badSOEmail=badSOEmail)

@app.route('/remove', methods=["GET", "POST"])
def remove():
    return render_template("remove.html")


@app.route('/remove_req',methods=['GET','POST'])
@login_required
def remove_req():
    username = current_user.username
    try:
        remReqs = AppUsers.query.filter_by(username=username).all()
        for remReq in remReqs:
            db.session.delete(remReq)
            db.session.commit()
    except:
        print 'no record found'
    return '{ "status" : 200 }'



@app.route('/add',methods=['GET','POST'])
def add():
    uData = request.get_json()
    username = uData['username']
    email = uData['email']
    emailSO = uData['emailSO']
    password = uData['pass']
    emailLen = len(email)
    emailSOLen = len(emailSO)
    dt = datetime.datetime.utcnow()
    email2, emailXs=make8(email)
    emailSO2, emailSOXs=make8(emailSO)
    obj = DES.new(EMAIL_KEY, DES.MODE_ECB)
    ciph = obj.encrypt(email2)
    ciph = ciph.decode('Latin-1')
    obj2 = DES.new(EMAIL_KEY, DES.MODE_ECB)
    ciph2 = obj2.encrypt(emailSO2)
    ciph2 = ciph2.decode('Latin-1')
    sendEmail(email,'add')
    newUser = AppUsers(username=username, password=password, dt=dt, crypEmail=ciph, uData=None)
    db.session.add(newUser)
    db.session.commit()
    login_user(newUser, remember=True)
    #send email
    
    uId = current_user.id
    newMulti = Multi(
                    uId=uId,
                    dt=dt,
                    ciph=ciph,
                    origLen = emailLen,
                    me=1
                )
    db.session.add(newMulti)
    db.session.commit()
    newMulti = Multi(
                    uId=uId,
                    dt=dt,
                    ciph=ciph2,
                    origLen = emailSOLen,
                    me=0
                )
    db.session.add(newMulti)
    db.session.commit()
    return '{ "status" : 200 }'

@app.route('/readd',methods=['GET','POST'])
def readd():
    uData = request.get_json()
    email = uData['email']
    sendEmail(email,'add')
    return '{"status" : 200}'

@app.route('/multi',methods=['GET','POST'])
@login_required
def multi():
    multi = request.get_json()
    dt = datetime.datetime.utcnow()
    if current_user.email_confirmed <1:
        print 'hit the error#########################'
        return  '{ "status" : "emailNotConfirmed" }'
    else:
        username = current_user.username
        user = AppUsers.query.filter_by(username=username).first()
        uId = user.id
        for email in multi[0]:
            email2 = multi[0][email]
            emailLen = len(email2)
            email2, x = make8(email2)
            obj = DES.new(EMAIL_KEY, DES.MODE_ECB)
            ciph = obj.encrypt(email2)
            ciph = ciph.decode('Latin-1')
            newMulti = Multi(
                            uId=uId,
                            ciph=ciph,
                            origLen = emailLen,
                            me=1
                        )
            db.session.add(newMulti)
            db.session.commit()
        for email in multi[1]:
            email2 = multi[1][email]
            emailLen = len(email2)
            email2, x = make8(email2)
            obj = DES.new(EMAIL_KEY, DES.MODE_ECB)
            ciph = obj.encrypt(email2)
            ciph = ciph.decode('Latin-1')
            newMulti = Multi(
                            uId=uId,
                            dt = dt,
                            ciph=ciph,
                            origLen = emailLen,
                            me=0
                        )
            db.session.add(newMulti)
            db.session.commit()
        myId = current_user.id
        you, SO = getMatches(uId)
        if SO:
            SO = SO[0]
            you = you[0]
            sendEmail(you,'match', SO=SO)
            sendEmail(SO,'match', SO=you)
        return '{ "status" : "good" }'

@app.route('/post_story',methods=['GET','POST'])
def post_story():
    story = request.get_json()
    username = current_user.username
    dt = datetime.datetime.utcnow()
    story['upvotes'] = 1
    story['downvotes'] = 0
    newStory = Stories(
                    details=story,
                    dt=dt,
                    username=username
                )
    db.session.add(newStory)
    db.session.commit()
    return '{ "status" : 200 }'


@app.route('/post_votes',methods=['GET','POST'])
def post_votes():
    data = request.get_json()
    id=data['id']
    upDown=data['upDown']
    username = current_user.username
    dt = datetime.datetime.utcnow()
    alreadyVoted = Votes.query.filter_by(sId=id,username=username).first()
    if alreadyVoted:
        print 'already voted'
    else:
        oldDetails = Stories.query.filter_by(id=id).first().details
        if upDown > 0:
            oldDetails['upvotes']+=1
        else:
            oldDetails['downvotes']+=1
        db.session.query(Stories).filter_by(id=id).update({"details": oldDetails})
        db.session.commit()
        newVote = Votes(
                    sId=id,
                    vote=upDown,
                    dt=dt,
                    username=username
                )
        db.session.add(newVote)
        db.session.commit()
    return '{ "status" : 200 }'

###############################################sql #######################################################################
##############################################################################################################################

@app.route('/sql')
def sql():
    print session['badSOEmail']

    # appls = Appls.query.all()
    # data = Appls.query.all()
    # data2 = Appls.query.filter_by(email = 'mritchie712@gmail.com')
    # data2 = Appls.query.filter_by(email = 'mritchie712@gmail.com')
    # q = db.session.query(Appls).filter_by(email = 'mritchie712@gmail.com').first()
    # q = Appls.query.all()
    # username = current_user.username
    # user = AppUsers.query.filter_by(username=username).first()
    # uId = user.id
    # myRecords = Multi.query.filter_by(uId=uId).all()
    # myId = current_user.id
    
    # you, SO = getMatches(myId)
    # SO = SO[0]
    # you = you[0]
    # sendMatchEmail(you, SO)

    return render_template('sql.html')
if __name__ == '__main__':
    # app.run()
    app.run(host='0.0.0.0', port=8000)


