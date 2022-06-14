#!/usr/bin/env python

from fileinput import filename
import gzip
import json
import requests
import os
from datetime import datetime


from elasticsearch import Elasticsearch

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


# Create the ES client instance
es = Elasticsearch("http://localhost:9200")

event_types = [
    'PushEvent',
    'IssueCommentEvent',
    'IssuesEvent',
    'PullRequestReviewCommentEvent',
    'PullRequestEvent']



for year in range(2015, 2023):

    es_index = "rh-events-{}".format(year)

    for month in range(1,13):
        for day in range(1,32):

            matched = 0
            unmatched = 0

            for hour in range(0,24):

                file_name = '{}-{:02d}-{:02d}-{}.json.gz'.format(year, month, day, hour)
                print('Processing {}'.format(file_name))

                # Download from GH Archive
                dl_url = 'https://data.gharchive.org/'+file_name

                try:
                    print('Downloading '+dl_url)
                    dl_file = requests.get(dl_url, stream=True,headers={'User-agent': 'Mozilla/5.0'})

                    if dl_file:
                        open(file_name, 'wb').write(dl_file.content)
                    else:
                        print("Skipping {}, HTTP response {}".format(file_name, dl_file.status_code))
                        continue

                    with gzip.open(file_name, 'rb') as archive:
                        lines = archive.readlines()

                        for line_json in lines:
                            event = json.loads(line_json)
                            if event['type'] in event_types:
                                if event['actor']['login'] in gh_users:
                                    # print('Found matched Red Hat user '+event['actor']['login'])

                                    resp = es.index(index=es_index, document=event)
                                    # print(resp['result'])

                                    matched = matched+1
                                    continue;
                                if event['type'] == 'PushEvent':
                                    for commit in event['payload']['commits']:
                                        if '@redhat.com' in commit['author']['email']:
                                            # print('Found UNmatched Red Hat user '+event['actor']['login']+' '+commit['author']['email'])
                                            resp = es.index(index=es_index, document=event)

                                            unmatched = unmatched+1
                                            break;
                    
                    os.remove(file_name)
                except Exception as e:
                    print(e)
                    print('Skipping {}'.format(file_name))
                    
                    with open('download_errors', 'a') as errors:
                        errors.write('{}: {} failed.'.format(datetime.now(), file_name))


            print('Found {} matched and {} unmatched records'.format(matched, unmatched))

                

