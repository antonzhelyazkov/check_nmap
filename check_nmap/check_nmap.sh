#!/bin/bash

CHECK_URL_BASE='http://87.120.207.136:5003/check_host'

usage() {
  echo "Usage: $0 [ -n IP ]" 1>&2 
}

exit_abnormal() {
  usage
  exit 1
}

while getopts ":n:" options; do

  case "${options}" in
    n)
      IP=${OPTARG}
      re_isanum='^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'
      if ! [[ $IP =~ $re_isanum ]] ; then
        echo "Error: TIMES must be a positive, whole number."
        exit_abnormal
        exit 1
      fi
      ;;
    :)
      echo "Error: -${OPTARG} requires an argument."
      exit_abnormal
      ;;
    *)
      exit_abnormal
      ;;
  esac

done

if ! [ -x "$(command -v jq)" ]
then
  echo 'Error: jq is not installed.' >&2
  exit 1
fi

CHECK_URL=$CHECK_URL_BASE/$IP
URL_RESP=`curl -sk $CHECK_URL`

if [ `echo $URL_RESP | jq .status` == 'true' ]
then
  echo `echo $URL_RESP | jq .msg`
  exit 0
else
  echo `echo $URL_RESP | jq .msg`
  exit 1
fi

exit 0