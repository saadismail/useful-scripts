## Written by Saad Ismail - me@saadismail.net
## https://github.com/saadismail

# Requirement:
#     - pdns and pdns-recursor installed
#     - pdns running on 5300 and pdns has webapi enabled and running on port 8081

# Usage:
# - server is an authoratative server and also have to serve local zones (https://doc.powerdns.com/authoritative/guides/recursion.html)
# - pdns-recursor forwards all zones hosted on pdns to pdns, and others to recursive servers
# - pdns-recursor requires pdns hosted zones to be mentioned explicitly which can be cumbersome to manage
# - this script keeps forwarded zones in sync with pdns host zones (can be used in cronjob)

# Cron (this is placed in /usr/sbin/powerdns and script runs every 30 minutes):
# - 0,30 * * * * /usr/bin/python3 /usr/sbin/powerdns.py > /etc/powerdns/forward.conf && systemctl restart pdns-recursor.service

# pdns-recursor config (only snippet):
# config-dir=/etc/powerdns
# hint-file=/usr/share/dns/root.hints
# include-dir=/etc/powerdns/recursor.d
# quiet=yes
# security-poll-suffix=
# setgid=pdns
# setuid=pdns
# allow-from=0.0.0.0/0
# local-address=0.0.0.0
# local-port=53
# forward-zones-file=/etc/powerdns/forward.conf

import json
import requests

POWERDNS_API_ENDPOINT = "http://127.0.0.1:8081/api/v1/servers/localhost/zones"
POWERDNS_API_KEY = "API_PASSWORD_HERE"
POWERDNS_API_REQUEST_HEADERS = { "X-API-Key": POWERDNS_API_KEY }
ZONE_FILE_LINE_SUFFIX = "=127.0.0.1:5300\n"


def get_zone_name_generator():
    r = requests.get(POWERDNS_API_ENDPOINT, headers=POWERDNS_API_REQUEST_HEADERS)
    http_body = r.text
    zones = json.loads(http_body)
    return ( zone['name'] for zone in zones )


def get_forward_zone_file_content(zone_name_generator):
    forward_zone_file_content = ""
    for zone_name in zone_name_generator:
        forward_zone_file_content += zone_name + ZONE_FILE_LINE_SUFFIX

    return forward_zone_file_content


zone_name_generator = get_zone_name_generator()
zone_file_content = get_forward_zone_file_content(zone_name_generator)
print(zone_file_content)