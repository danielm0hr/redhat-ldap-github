#/bin/bash

ldapsearch -x -H ldap://ldap.corp.redhat.com \
    -b dc=redhat,dc=com -W "objectclass=person" \
    cn rhatSocialURL rhatRnDComponent manager rhatProject\
         > ldap_tree
