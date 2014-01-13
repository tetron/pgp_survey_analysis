#!/usr/bin/env python

import pgp_survey
import re
import arvados
import pprint

surveys_directory = "surveys"

print("Reading surveys")
# Input trait surveys and list of traits.
trait_surveys, trait_survey_traits = pgp_survey.get_trait_surveys(surveys_directory)

all_traits = {}
for a in trait_survey_traits:
    for b in a:
        all_traits[b] = None

# Input participant survey.
participant_survey = pgp_survey.get_participant_survey(surveys_directory)

huIDs = list(participant_survey.get_huIDs())

api = arvados.api('v1')

print("Initializing from database")

traits_query = api.traits().list(limit=100000).execute()["items"]

for a in traits_query:
    all_traits[a["name"]] = a

humans_query = api.links().list(limit=100000, where={"head_kind":"arvados#human", "link_class": "identifier", "name": huIDs}).execute()["items"]
humans = {}
for a in humans_query:
    humans[a["name"]] = a

survey_columns = {}
for i in xrange(0, len(participant_survey.header_titles)):
    survey_columns[participant_survey.header_titles[i]] = i

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
    
    #for i in xrange(0, len(participant_survey.header_titles)):
    #    if len(participant_survey.get_latest_responses(huID)[i].strip()) > 0:
    #        print("{2}) {0}: {1}".format(participant_survey.header_titles[i], participant_survey.get_latest_responses(huID)[i], i))

    hutraits_query = api.links().list(where={"name": "pgp-survey-response",
                                             "link_class": "human_trait",
                                             "tail_uuid": humans[huID]["head_uuid"]}).execute()["items"]

    hutraits = pgp_survey.get_traits_for(huID, participant_survey, trait_surveys, trait_survey_traits)

    already_added_traits = [t["head_uuid"] for t in hutraits_query]

    for ht in hutraits:
        if ht not in all_traits or all_traits[ht] == None:
            print("Creating trait {0}".format(ht))
            all_traits[ht] = api.traits().create(body={"trait": {"name": ht}}).execute()

        if all_traits[ht]["uuid"] not in already_added_traits:
            print("{0}/{2}: Adding trait '{1}'".format(huID, ht, humans[huID]["head_uuid"]))

            l = api.links().create(body={"link": {"head_uuid": all_traits[ht]["uuid"],
                                                  "head_kind": "arvados#trait",
                                                  "tail_uuid": humans[huID]["head_uuid"], 
                                                  "tail_kind": "arvados#human",
                                                  "link_class": "human_trait",
                                                  "name": "pgp-survey-response",
                                                  "properties": {"value": "Y"}
                                                  }}).execute()

    for ht in survey_columns:
        if ht == 'Sex/Gender' or ht == 'Race/Ethnicity':
            if all_traits[ht]["uuid"] not in already_added_traits:
                print("{0}/{2}: Adding trait '{1}'".format(huID, ht, humans[huID]["head_uuid"]))

                l = api.links().create(body={"link": {"head_uuid": all_traits[ht]["uuid"],
                                                      "head_kind": "arvados#trait",
                                                      "tail_uuid": humans[huID]["head_uuid"], 
                                                      "tail_kind": "arvados#human",
                                                      "link_class": "human_trait",
                                                      "name": "pgp-survey-response",
                                                      "properties": {"value": participant_survey.get_latest_responses(huID)[survey_columns[ht]] }
                                                      }}).execute()
            
        
