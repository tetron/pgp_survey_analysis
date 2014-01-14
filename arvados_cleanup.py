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
