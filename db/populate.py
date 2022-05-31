#!/usr/bin/env python

import gzip
import json

gh_users = set()

with open('ldap_tree') as ldap:
    lines = ldap.readlines()

    for line in lines:
        if line.startswith('rhatSocialURL: Github->'):
            gh_users.add(line.split('/')[-1].strip())


with gzip.open('../gharchive/2015-01-01-0.json.gz', 'rb') as archive:
    lines = archive.readlines()

    for line_json in lines:
        event = json.loads(line_json)
        if event['type'] == 'PushEvent' and event['actor']['login'] in gh_users:
            print("Found Red Hat user "+event['actor']['login'])
            # print(event['payload'])
