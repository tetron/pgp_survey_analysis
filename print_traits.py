#!/usr/bin/env python

import pgp_survey
import re

surveys_directory = "surveys"

# Input trait surveys and list of traits.
trait_surveys, trait_survey_traits = pgp_survey.get_trait_surveys(surveys_directory)

# Input participant survey.
participant_survey = pgp_survey.get_participant_survey(surveys_directory)

for huID in participant_survey.get_huIDs():
    print(huID)
    #for i in xrange(0, len(participant_survey.header_titles)):
    #    print("{0}: {1}".format(participant_survey.header_titles[i], participant_survey.get_latest_responses(huID)[i]))
    print(pgp_survey.get_traits_for(huID, participant_survey, trait_surveys, trait_survey_traits))
