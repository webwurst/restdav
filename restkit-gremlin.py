# -*- coding: utf-8 -*-

from restkit import Resource
import json


class GremlinGraph(Resource):

    def __init__(self, base_uri='http://localhost:8182/graphs/', database='emptygraph', **kwargs):
        super(Rexster, self).__init__(base_uri+database, follow_redirect=False, **kwargs)
        
        # ^redirects sollten nicht vorkommen
        # was für kwargs möglich?
 

    def query(self, query=None):

        payload = json.dumps({u'script': query}, ensure_ascii=False) # liefert so unicode
        headers = {'Content-Type': 'application/json'}
        resp = self.post('/tp/gremlin', headers=headers, payload=payload)

        return json.loads(resp.body_string()) 
        # evtl. erst bei zugriff explizit auslesen und wandeln?
        # falls das ergebnis direkt über bottle, z.b. rausgeht, dann wäre file-like eleganter

