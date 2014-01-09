#!/usr/bin/env python

import urllib2
from datetime import datetime

surveys = { 8: "Blood",
            6: "Cancers",
            11: "CirculatorySystem",
            17: "CongenitalTraitsAndAnomalies",
            13: "DigestiveSystem",
            7: "Endocrine,Metabolic,Nutritional,AndImmunity",
            14: "GenitourinarySystems",
            16: "MusculoskeletalSystemAndConnectiveTissue",
            9: "NervousSystem",
            12: "RespiratorySystem",
            15: "SkinAndSubcutaneousTissue",
            10: "VisionAndHearing"
}

s1 = urllib2.urlopen("https://my.personalgenomes.org/google_surveys/1/download")
now = datetime.now().strftime("%Y%m%d%H%M%S")
f = open("PGPParticipantSurvey-{0}.csv".format(now), 'w')
f.write(s1.read())
f.close()
s1.close()

for n, t in surveys.items():
    s1 = urllib2.urlopen("https://my.personalgenomes.org/google_surveys/{0}/download".format(n))
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    f = open("PGPParticipantSurvey-{1}-{0}.csv".format(now, t), 'w')
    f.write(s1.read())
    f.close()
    s1.close()
