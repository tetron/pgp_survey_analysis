#!/usr/bin/env python

import pgp_survey
import re
import arvados
import pprint

surveys_directory = "surveys"

print("Reading surveys")
# Input trait surveys and list of traits.
trait_surveys, trait_survey_traits = pgp_survey.get_trait_surveys(surveys_directory)

# Dict of trait names (from PGP survey) to trait Dicts (must be filled in)
all_traits = {}
for a in trait_survey_traits:
    for b in a:
        all_traits[b] = None

# Input participant survey.
participant_survey = pgp_survey.get_participant_survey(surveys_directory)

huIDs = list(participant_survey.get_huIDs())

api = arvados.api('v1')

print("Getting traits list from database")

traits_query = api.traits().list(limit=100000).execute()["items"]

# Fill in all_traits with trait Dicts already in database
for a in traits_query:
    all_traits[a["name"]] = a

print("Getting humans list from database")

humans_query = api.links().list(limit=100000, where={"head_kind":"arvados#human", "link_class": "identifier", "name": huIDs}).execute()["items"]

# Dict of PGP huID to arvados link record that associates the human uuid (head_uuid entry) with the PGP huID (name entry)
humans = {}
for a in humans_query:
    humans[a["name"]] = a

# Dict of survery column title to column position
survey_columns = {}
for i in xrange(0, len(participant_survey.header_titles)):
    survey_columns[participant_survey.header_titles[i]] = i

# List of human uuids (head_uuid) from humans Dict
human_uuids = [humans[h]["head_uuid"] for h in humans]

print("Getting humans/trait links from database")

hutraits_query = api.links().list(limit=100000,
                                  where={"name": "pgp-survey-response",
                                         "link_class": "human_trait",
                                         "tail_uuid": human_uuids}).execute()["items"]

# Dict of human uuid to list of Dicts for links to traits
hutraits_db = {}
for t in hutraits_query:
    if t["tail_uuid"] not in hutraits_db:
        hutraits_db[t["tail_uuid"]] = []
    hutraits_db[t["tail_uuid"]].append(t)

#pprint.pprint(hutraits_db)

ct = 0
for huID in huIDs:
    ct = ct + 1
    print("Checking {0} ({1}/{2})".format(huID, ct, len(huIDs)))

    if huID not in humans:
        print("Adding {0} to metadata database".format(huID))
        h = api.humans().create(body={"human": {}}).execute()
        humans[huID] = api.links().create(body={"link": {"head_uuid": h["uuid"], 
                                                         "head_kind": "arvados#human",
                                                         "link_class": "identifier",
                                                         "name": huID 
                                                         }}).execute()

    human_uuid = humans[huID]["head_uuid"]
    
    hutraits = pgp_survey.get_traits_for(huID, participant_survey, trait_surveys, trait_survey_traits)

    # list of trait uuids that are linked to this human uuid
    already_added_traits = []
    if human_uuid in hutraits_db:
        already_added_traits = [t["head_uuid"] for t in hutraits_db[human_uuid]]
        #pprint.pprint(already_added_traits )
    else:
        hutraits_db[human_uuid] = []
        
    for ht in hutraits:
        if ht not in all_traits or all_traits[ht] == None:
            print("Creating trait {0}".format(ht))
            all_traits[ht] = api.traits().create(body={"trait": {"name": ht}}).execute()

        #pprint.pprint(all_traits[ht])
        if all_traits[ht]["uuid"] not in already_added_traits:
            print("{0}/{2}: Adding trait '{1}'".format(huID, ht, humans_uuid))

            hutraits_db[human_uuid].append(api.links().create(body={"link": {"head_uuid": all_traits[ht]["uuid"],
                                                  "head_kind": "arvados#trait",
                                                  "tail_uuid": humans_uuid, 
                                                  "tail_kind": "arvados#human",
                                                  "link_class": "human_trait",
                                                  "name": "pgp-survey-response",
                                                  "properties": {"value": "Y"}
                                                  }}).execute())

    for ht in survey_columns:
        if ht == 'Sex/Gender' or ht == 'Race/ethnicity':
            if all_traits[ht]["uuid"] not in already_added_traits:
                print("{0}/{2}: Adding trait '{1}'".format(huID, ht, humans_uuid))

                hutraits_db[human_uuid].append(api.links().create(body={"link": {"head_uuid": all_traits[ht]["uuid"],
                                                      "head_kind": "arvados#trait",
                                                      "tail_uuid": humans[huID]["head_uuid"], 
                                                      "tail_kind": "arvados#human",
                                                      "link_class": "human_trait",
                                                      "name": "pgp-survey-response",
                                                      "properties": {"value": participant_survey.get_latest_responses(huID)[survey_columns[ht]] }
                                                      }}).execute())

    # Set ownership to PGP Data group
    pgp_group_owner = {"owner_uuid": "qr1hi-j7d0g-it30l961gq3t0oi"}
    api.humans().update(uuid=human_uuid, body=pgp_group_owner).execute()
    api.links().update(uuid=humans[huID]['uuid'], body=pgp_group_owner).execute()
    for t in hutraits_db[human_uuid]:
        api.links().update(uuid=t['uuid'], body=pgp_group_owner).execute()

for t in all_traits:
    if all_traits[t] != None:
        api.traits().update(uuid=all_traits[t]["uuid"], body=pgp_group_owner).execute()
