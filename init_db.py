import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON, JSONB
import json
from cb import db, Faqs, Stories, AppUsers


def init_db():
    dt = datetime.datetime.utcnow()
    faqsJson = json.loads(open("faq.json").read())
    stories = json.loads(open("stories.json").read())
    print 'JSONs Loaded'
    db.reflect()
    db.drop_all()
    db.session.commit()
    print 'all dropped, shit!'
    db.create_all()
    db.session.commit()
    print 'all created, OK!'
    for faq in faqsJson:
        newFaq = Faqs(
            details=faq)
        db.session.add(newFaq)
        db.session.commit()
    for story in stories:
        username = story['username']
        newStory = Stories(
            details=story,
            dt=dt,
            username=username)
        db.session.add(newStory)
        db.session.commit()
    print 'JSONs to Tables'
