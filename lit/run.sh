#!/bin/bash
cat /data/input.log
/usr/share/logstash/bin/logstash \
    -e "input { stdin { codec => json_lines } }" < "/data/input.log"
