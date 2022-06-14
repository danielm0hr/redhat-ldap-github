#!/usr/bin/env python

from fileinput import filename

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

result_size=1000

for user in gh_users:
    print(user)
    result_from=0

    while True:
        resp = es.search(index="rh-events-2015", from_=result_from, size=result_size, query={
                "match": {
                    "actor.login": {
                        "query": user
                    }
                }
            })

        for doc in resp['hits']['hits']:
            update_resp = es.update(index="rh-events-2015", id=doc['_id'],doc={
                    "redhat.uid": gh_users[user]['uid'],
                    "redhat.rnd_comp": gh_users[user]['rh_rnd_comp'],
                    "redhat.project": gh_users[user]['rh_project'],
                    "redhat.manager": gh_users[user]['manager_uid']
                })

            # print(doc['_id'])

        result_from += result_size
        if result_from >= resp['hits']['total']['value']:
            break


    # print("User "+user+":")
    # print("Got %d Hits:" % resp['hits']['total']['value'])
    # print(resp)



