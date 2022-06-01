#!/usr/bin/env python

import gzip
import json
import requests

from datetime import datetime

gh_users = dict()

with open('ldap_tree') as ldap:
    lines = ldap.readlines()

    uid = gh_id = rh_rnd_comp = rh_project = manager_uid = str()

    for line in lines:
        if line.startswith('dn: uid='):
             uid = line.split('=')[1].split(',')[0]

        if line.startswith('rhatSocialURL: Github->'):
            gh_id = line.split('/')[-1].strip()

        if line.startswith('rhatRnDComponent: '):
            rh_rnd_comp = line.split(':', 1)[1].strip()

        if line.startswith('rhatProject: '):
            rh_project = line.split(':', 1)[1].strip()

        if line.startswith('manager: '):
            manager_uid = line.split('=')[1].split(',')[0]

        if line.isspace():
            # End of user entry. If no Github id found: Skip. Otherwise add.
            if gh_id:
                if not rh_rnd_comp: rh_rnd_comp = 'Other'
                if not rh_project: rh_project = 'Other'

                gh_users[gh_id]= {
                                    'uid': uid,
                                    'rh_rnd_comp': rh_rnd_comp,
                                    'rh_project': rh_project,
                                    'manager_uid': manager_uid
                                }

                # print('Added '+gh_id+': ')
                # print(gh_users[gh_id])

            # Reinitialize vars for next user entry    
            uid = gh_id = rh_rnd_comp = rh_project = manager_uid = str()

# for year in range(2015, 2022):
#     for month in range(1,12):
#         for day in range(1,31):
#             for hour in range(0,23):

#                 file_name = '{}-{:02d}-{:02d}-{}.json.gz'.format(year, month, day, hour)
#                 dl_url = 'https://data.gharchive.org/'+file_name

#                 print('Downloading '+dl_url)
#                 dl_file = requests.get(dl_url, stream=True,headers={'User-agent': 'Mozilla/5.0'})
#                 open(file_name, 'wb').write(dl_file.content)

#                 with gzip.open(file_name, 'rb') as archive:
#                     lines = archive.readlines()

#                     for line_json in lines:
#                         event = json.loads(line_json)
#                         if event['type'] == 'PushEvent' and event['actor']['login'] in gh_users:
#                             print("Found Red Hat user "+event['actor']['login'])
#                             # print(event['payload'])
