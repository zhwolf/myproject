# -*- coding: UTF-8 -*-
import settings
from sqlalchemy.orm import *
from sqlalchemy.orm import scoped_session
from sqlalchemy import *
import Queue

#for sqlalchemy
DATABASE_URL=settings.DBURL

#print "DATABASE_URL", DATABASE_URL

IfMSSQL= DATABASE_URL.lower().find('mssql') >=0

#engine = create_engine(DATABASE_URL, echo=False, has_window_funcs=IfMSSQL)
#engine = create_engine(DATABASE_URL, echo=False,convert_unicode=True,encoding='utf-8',assert_unicode=False)
engine = create_engine(DATABASE_URL, echo=False,pool_size=15,pool_recycle=15)

metadata = MetaData()
metadata.bind=engine
session_factory  = sessionmaker(autoflush=True,bind=engine)
Session = scoped_session(session_factory)
#SessionQueue = Queue.Queue()

def getSession():
#    if SessionQueue.empty():
#        session = Session()
#        SessionQueue.put(session)
#        print "create new sesson, now we have %s sesssions" %(SessionQueue.qsize())
#    a =SessionQueue.get()
    return Session()


def removeSession(session):
    session.expunge_all()
#    SessionQueue.put(session)
#    print "recycle sesson, now we have %s sesssions" %(SessionQueue.qsize())

class Any():
    pass

def update_model(model, fields, **kwds):
    """Update an object (like an SQLAlchemy model) from a dictionary (like
    that provided by form.cleaned_data). Since Django's ModelForm doesn't work
    with SQLAlchemy, this is a reasonably quick alternative approach::
        
        forms.update_model(user, form.cleaned_data, exclude=['password'])

    Provide either ``exclude`` or ``include`` to further restrict which fields
    are included. Fields with an underscore are also excluded.
    """
    
    if model== None:
        model = Any()
    exclude = kwds.pop('exclude', [])
    include = kwds.pop('include', [])
    for k, v in fields.items():
        if include and (k not in include):
            continue
        if hasattr(model, k) and not callable(getattr(model, k)) and k not in exclude:
            setattr(model, k, v)
            
#SessionQueue.put(Session())