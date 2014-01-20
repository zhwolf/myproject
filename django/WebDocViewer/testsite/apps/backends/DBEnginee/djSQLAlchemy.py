# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from django.conf import settings
from sqlalchemy.orm import *
from sqlalchemy.orm import scoped_session
from sqlalchemy.pool import StaticPool
import sqlalchemy
import Queue


#dialect+driver://username:password@host:port/database
#sqlalDB = {}
#sqlalDB['ENGINE'] = settings.DATABASES['default']['ENGINE'].split(".")[-1]
#sqlalDB['NAME'] = settings.DATABASES['default'].get('NAME', '').strip()
#if sqlalDB['ENGINE'] == 'sqlite3':
#    sqlalDB['ENGINE'] = 'sqlite'    
#    sqlalDB['NAME'] =  sqlalDB['NAME'].replace('\\', '/') 
#sqlalDB['USER'] = settings.DATABASES['default'].get('USER', '').strip()
#if sqlalDB['USER'] > '':
#    sqlalDB['PASSWORD'] = ':' + settings.DATABASES['default'].get('PASSWORD', '').strip() + '@'
#else:
#    sqlalDB['PASSWORD'] = ''    
#sqlalDB['HOST'] = settings.DATABASES['default'].get('HOST', '').strip()
#if sqlalDB['HOST'] > '':
#    sqlalDB['PORT'] = ':' + settings.DATABASES['default'].get('PORT', '').strip() + '/'
#else:
#    sqlalDB['PORT'] = '/'    
#
#DATABASE_URL= "%(ENGINE)s://%(USER)s%(PASSWORD)s%(HOST)s%(PORT)s%(NAME)s" % (sqlalDB)
#
#
#print "DATABASE_URL:",DATABASE_URL

#if sqlalDB['ENGINE'] == 'sqlite':
#    engine = create_engine(DATABASE_URL, echo=False)
#else:
#    engine = create_engine(DATABASE_URL, echo=False,pool_size=15,pool_recycle=15)    
    
from sqlalchemy.engine.url import URL
__all__ = ['metadata']
def a_create_engine():
    issqlite = False
    _engine = settings.DATABASES['default']['ENGINE'].split(".")[-1]
    _name = settings.DATABASES['default'].get('NAME', '').strip()
    issqlite = _engine in ['sqlite3', 'sqlite']
    if issqlite:
        _engine = 'sqlite'    
        _name = _name.replace('\\', '/') 
    url = URL(drivername= _engine,
              database= _name,
              username= settings.DATABASES['default'].get('USER', '') or None,
              password= settings.DATABASES['default'].get('PASSWORD', '') or None,
              host= settings.DATABASES['default'].get('HOST', '') or None,
              port= settings.DATABASES['default'].get('PORT', '') or None,
              query = settings.DATABASES['default'].get('OPTIONS', {}),
              )
    options = getattr(settings, 'SQLALCHEMY_OPTIONS', {})
    if issqlite:
        return  sqlalchemy.create_engine(url, echo=True,connect_args={'check_same_thread':False},
                    poolclass=StaticPool)
    else:        
        return  sqlalchemy.create_engine(url, echo=False,pool_size= 15,pool_recycle=15) 

engine = a_create_engine()
metadata = sqlalchemy.MetaData()
metadata.bind=engine
session_factory  = sessionmaker(autoflush=True,bind=engine)
Session = scoped_session(session_factory)

#def getSession():
#    return Session()

#def removeSession(session):
#    session.expunge_all()


def update_model(model, fields, **kwds):
    class Any():
        pass

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

