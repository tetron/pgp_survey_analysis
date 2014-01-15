#!/usr/bin/env python

import pgp_survey
import re
import arvados
import pprint

api = arvados.api('v1')

print("Getting links")
query = api.links().list(limit=100000, where={"link_class": "human_trait"}).execute()["items"]

def s(n):
    if n == None:
        return '___'
    else:
        return n

d = {}
for a in query:
    key = s(a["head_uuid"]) + s(a["tail_uuid"]) + s(a["link_class"]) + s(a["name"])
    if key not in d:
        d[key] = a
    else:
        print("{0} is redundant with {1}".format(a["uuid"], d[key]["uuid"]))
        api.links().delete(uuid=a["uuid"]).execute()

uuid_infix_object_kind = {
      '4zz18': 'arvados#collection',
      'tpzed': 'arvados#user',
      'ozdt8': 'arvados#api_client',
      '8i9sb': ' arvados#job',
      'o0j2j': 'arvados#link',
      '57u5n': 'arvados#log',
      'j58dm': 'arvados#specimen',
      'p5p6p': 'arvados#pipeline_template',
      'mxsvm': 'arvados#pipeline_template', # legacy Pipeline objects
      'd1hrv': 'arvados#pipeline_instance',
      'uo14g': 'arvados#pipeline_instance', # legacy PipelineInstance objects
      'j7d0g': 'arvados#group',
      'ldvyl': 'arvados#group' # only needed for legacy Project objects
    }


for a in query:
    delete = False
    m = re.search('.....-(.....)-...............', a['head_uuid'])
    for k, v in uuid_infix_object_kind.items():
        if m.group(1) == k and a['head_kind'] != v:
            print("{2} has a mismatch between uuid type {0} and head kind {1}".format(v, a['head_kind'], a['uuid']))
            delete = True

    m = re.search('.....-(.....)-...............', a['tail_uuid'])
    for k, v in uuid_infix_object_kind.items():
        if m.group(1) == k and a['tail_kind'] != v:
            print("{2} has a mismatch between uuid type {0} and tail kind {1}".format(v, a['tail_kind'], a['uuid']))
            delete = True

    if delete:
        api.links().delete(uuid=a['uuid']).execute()
        
