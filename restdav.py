#!/usr/bin/env python
# -*- coding: utf-8 -*-

### siehe auch http://code.google.com/p/wsgidav/wiki/ChangeLog04

from gevent import monkey; monkey.patch_all()
import gevent

from bottle import route
import bottle

import logging
from pprint import pprint
import inspect

import sys
from restkit import Resource
import restkit

from restkit.globals import set_manager, get_manager
from restkit.manager.mgevent import GeventManager

# set the gevent connection manager
set_manager(GeventManager())

# logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


# zu webdav
#
# für beispiel '207 Multi-Status' siehe
#   http://tools.ietf.org/html/rfc4437#page-13
#
# Header
#   Apply-To-Redirect-Ref Request Header
#
# apache kennt folgende methoden
#   'OPTIONS,GET,HEAD,POST,DELETE,TRACE,PROPFIND,PROPPATCH,COPY,MOVE,LOCK,UNLOCK'
#
#

# zu datenbank/restkit modulen
# restkit-gremlin
# restkit-sparql
# restkit-couchdb
# restkit-elasticsearch
# restkit-apachewebdav
#
# siehe auch https://github.com/benoitc/couchdbkit/blob/master/couchdbkit/resource.py#L104
# (ungefähr zeile 104)

import restkit-gremlin
from restkit import Resource


# next
#
# web-app
# create user, password
# create item/collection (in couchdb?)
# get/change meta, access-rights
# query collection
#
# restdav -> github


class RestdavDB(Resource):

    def create():
	    pass
    	    
    def query(id, uri, expand, user, type, ):
        # jeweils mehrzahl möglich
        pass
        
    def edit():
        pass
        
    def remove():
        pass
        

    # get collection, expand=False
    # liefert nur direkt unterhalb einer collection
    # zählt allerdings auch alle überhaupt unterhalb
    
    # auth_user
    # übergibt user und password oder hashed password?
    # liefert True/False
    
    # generell:
    # zu allen anfragen timestamp oder range möglich
    # zu allen anfragen base_uri möglich, nur unterhalb wird gesucht
    # zu allen anfragen user(s)/group(s) möglich.


# zu Auth
#
# geht das?
#   wenn normaler aufruf, dann ohne rechte durchführen
#   wenn @ in uri für auth, dann redirect mit auth-status-code?
#   oder login-query für browser
#   login-query auch für nautilus?
#   oder immer mit auth für nautilus
#
#   erstmal: nur auth


class ApacheWebdav(Resource):

    def __init__(self, **kwargs):
        uri = "http://localhost"
        super(ApacheWebdav, self).__init__(uri, **kwargs)


apdav = ApacheWebdav()

# den meisten kram in plugin auslagern?
# also login/out z.b.

@route('<path:path>', method=['GET', 'OPTIONS', 'PROPFIND', 'MKCOL', 'HEAD', 'PUT', 'MOVE', 'DELETE'])
def root(path):

#    if log.isEnabledFor(logging.DEBUG):
#        log.debug("")
#        log.debug("Request: {method} {path}".format(method=bottle.request.method, path=path))
#        for header, value in bottle.request.headers.items():
#            log.debug("  {header}: {value}".format(header=header, value=value))
#        log.debug("")

    if 'logout' in bottle.request.params:
        # redirect to anonymous user..
        # TODO
        bottle.redirect(path)

    if 'login' in bottle.request.params and 'Authorization' in bottle.request.headers:
        # redirect to same without login-query..
        # TODO
        bottle.redirect(path)



    if 'gvfs' in bottle.request.get_header('User-Agent', '') and 'Authorization' not in bottle.request.headers or 'login' in bottle.request.params:
        log.debug("============= gvfs and not auth ===================")
        bottle.response.headers['WWW-Authenticate'] = 'Basic realm="wrapdav"'
        bottle.abort(401, 'Access Denied. You need to login first.')
    


    if bottle.request.method in ['GET', 'PROPFIND']:
        if path.find('/gila') == 0 and bottle.request.auth[0] != 'gila':
            bottle.abort(403, 'Forbidden')
    
        if path.find('/webwurst') == 0 and bottle.request.auth[0] != 'webwurst':
            bottle.abort(403, 'Forbidden')
        
    try:
        # The following HTTP/1.1 headers are hop-by-hop headers: Connection, Keep-Alive, Proxy-Authenticate, Proxy-Authorization, TE, Trailers, Transfer-Encoding, Upgrade

        headers = {h : i for h, i in bottle.request.headers.items()}

        if 'Content-Length' in headers: del headers['Content-Length']
#        if 'Connection' in headers: del headers['Connection']
#       ^ sonst probleme bei mkcol..

        if 'Keep-Alive' in headers: del headers['Keep-Alive']
        if 'Accept-Encoding' in headers: del headers['Accept-Encoding'] # gzip oder so
        if 'Accept-Charset' in headers: del headers['Accept-Charset'] # am besten utf-8
#        if 'Host' in headers: del headers['Host']
#       ^ sonst probleme bei mkcol..

        if 'Accept-Language' in headers: del headers['Accept-Language']
        
        resp = apdav.request(bottle.request.method, path, payload=bottle.request.body, headers=headers)
        # ^payload gets file-like object
        
        body = resp.body_stream()
        
    except restkit.errors.ResourceNotFound:
        print "restkit.errors.ResourceNotFound"
        pass
    except restkit.errors.Unauthorized:
        print "restkit.errors.Unauthorized"
        pass
    except restkit.errors.RequestFailed as e:
        print "restkit.errors.RequestFailed"
        body = e.msg # is resp.body_string()
        resp = e.response
    except restkit.errors.RequestFailed:
        pass
    except:
        print "<pre>Unexpected error:"+ str(sys.exc_info()[0]) +"</pre>"


    bottle.response.status = resp.status #_int
    for h, i in resp.headers.items():
        if h in ['CONTENT-ENCODING']:
            continue
        bottle.response.set_header(h, i)
        

    # ^return file-like object    
    return body




#from restkit.contrib.wsgi_proxy import HostProxy

#proxy = HostProxy("http://127.0.0.1:80")


@route('/hello')
def hello():
    return "Hello World!"

bottle.debug(True)
bottle.run(host='localhost', port=8080, reloader=True, server='gevent')


# application = bottle.default_app()
