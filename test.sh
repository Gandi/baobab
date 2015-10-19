#!/bin/bash
# simple script that check all api route for a http_ok 200.
# this script use the same version as the prod do.
# this is due of testypie < 0.9.12: hasn't unit test build in
# this is MANDATORY and should be run at least before tagging

SERVER_URL='127.0.0.1:4242'

function kill_server()
{
    pid=$(netstat -nlpt | grep $SERVER_URL | awk '{print $7}' | cut -d / -f 1)
    # pid=$(lsof -ti @${SERVER_URL}) # no lsof in jenkins
    if [ -n "${pid}" ]
    then
        kill $pid
    fi
}

function clean()
{
    kill_server
    deactivate

    if [ "${do_clean}" -ne 0 -o "$1" -ne 0 ]
    then
      exit 1
    fi

    rm -rf "$venv"

    # re-use the normale defaul.db
    rm -f "${db_file}"
    if [ -e "${db_file}.old" ]
    then
        mv "${db_file}.old" "${db_file}"
    fi

    echo 'ALL TEST ARE OK'
    exit 0
}

function check_http_code()
{
    content_type=$1
    url=$2
    http_code=$3
    res_code=$4

    if [ "${res_code}" != "${http_code}" ]
    then
        echo "Error route (${content_type}): ${url} http_code is: " \
            "${res_code} should be ${http_code}"
        pip freeze
        clean 1
    fi
}

function init_db()
{
    db_file=$(python <<-EOF
		import os
		os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baobab.settings')
		from django.conf import settings
		print settings.DATABASES['default']['NAME']
		EOF
    )

    if [ "$1" -ne 0 ]
    then
      return
    fi

    if [ -e "${db_file}" ]
    then
      mv "${db_file}" "${db_file}.old"
    fi

    # setup the db
    baobab setup-dev
}

do_clean=$#
venv="test-prod-$(date +%F)"
if [ ! -e "${venv}" ]
then
    # create a venv
    virtualenv "$venv"
    source "$venv/bin/activate"

    # install baboab with the same version of tastypie as the prod
    pip install 'Django==1.4.5'
    pip install 'django-tastypie==0.9.10'
    pip install -e '.[dev,test]'
    python setup.py develop

    init_db 0
else
    source "$venv/bin/activate"
    init_db 1
fi

kill_server
# run the server
baobab runserver $SERVER_URL &

echo 'Wait for the server to be ready ...'
sleep 5

echo '*** BEGINNING OF THE TEST ***'

# check the api route for 200 for json
for url in 'api/events' 'api/events?services=IAAS' \
                        'api/events?category=Incident' \
                        'api/events?services=IAAS&category=Incident' \
                        'api/events?date_end=null' \
                        'api/events?current=true' \
                        'api/events?current=false' \
                        'api/services' 'api/status'
do
    res=$(curl -H 'Accept: application/json' -s -o /dev/null \
        -w '%{http_code}' "127.0.0.1:4242/${url}")
    check_http_code 'json' "${url}" "200" "${res}"
done

# check the api route for 200 for html
for url in 'api/events' 'api/events?services=IAAS' \
                        'api/events?category=Incident' \
                        'api/events?services=IAAS&category=Incident' \
                        'api/events?date_end=null' \
                        'api/events?current=true' \
                        'api/events?current=false' \
                        'api/services' 'api/status'
do
    res=$(curl -H 'Accept: text/html' -s -o /dev/null \
        -w '%{http_code}' "127.0.0.1:4242/${url}")
    check_http_code 'http' "${url}" '200' "${res}"
done

# check the api schema route for 200 for json
for url in 'api' 'api/events/schema' 'api/services/schema' 'api/status/schema'
do
    res=$(curl -H 'Accept: application/json' -s -o /dev/null \
        -w '%{http_code}' "127.0.0.1:4242/${url}")
    check_http_code 'json' "${url}" '200' "${res}"
done

# check the api schema route for 200 for html
for url in 'api' 'api/events/schema' 'api/services/schema' 'api/status/schema'
do
    res=$(curl -H 'Accept: text/html' -s -o /dev/null \
        -w '%{http_code}' "127.0.0.1:4242/${url}")
    check_http_code 'http' "${url}" '200' "${res}"
done

# check nested bundle for json
url='api/events/1'
res=$(curl -H 'Accept: application/json' -s -o /dev/null \
    -w '%{http_code}' "127.0.0.1:4242/${url}")
check_http_code 'json' "${url}" '200' "${res}"

# check nested bundle for json
url='api/events/1'
res=$(curl -H 'Accept: text/html' -s -o /dev/null \
    -w '%{http_code}' "127.0.0.1:4242/${url}")
check_http_code 'http' "${url}" '200' "${res}"

# check lang
url='api/events/2'
res=$(curl -si -H 'Accept-Language: fr' "127.0.0.1:4242/${url}" | \
      tr -d '\r' | grep -i 'Content-Language' | awk '{print $2}')
check_http_code 'content_type: fr' "${url}" 'fr' "${res}"

res=$(curl -si -H 'Accept-Language: fr' "127.0.0.1:4242/${url}" | \
    tr -d '\r' | grep -i 'un filter est tomb')
if [ -z "${res}" ]
then
    check_http_code 'Fr event' "${url}" 'un filter est tomb' 'EMPTY'
fi

res=$(curl -si -H 'Accept-Language: fr' "127.0.0.1:4242/${url}" | \
    tr -d '\r' | grep -i 'une partie est re-disponible')
if [ -z "${res}" ]
then
    check_http_code 'Fr log 1/2' "${url}" \
        'une partie est re-disponible' 'EMPTY'
fi

res=$(curl -si -H 'Accept-Language: fr' "127.0.0.1:4242/${url}" | \
    tr -d '\r' | grep -i 'tout est ok')
if [ -z "${res}" ]
then
    check_http_code 'Fr log 1/2' "${url}" 'tout est ok' 'EMPTY'
fi

# check fallback en
res=$(curl -si -H 'Accept-Language: es' "127.0.0.1:4242/${url}" | \
      tr -d '\r' | grep -i 'Content-Language' | awk '{print $2}')
check_http_code 'content_type: es' "${url}" 'en' "${res}"

# check RSS Feed
url='rss/'
res=$(curl -H 'Accept: text/html' -s -o /dev/null \
    -w '%{http_code}' "127.0.0.1:4242/${url}")
check_http_code 'http' "${url}" '200' "${res}"

# Check Atom Feed
url='atom/'
res=$(curl -H 'Accept: text/html' -s -o /dev/null \
    -w '%{http_code}' "127.0.0.1:4242/${url}")
check_http_code 'http' "${url}" '200' "${res}"

echo '*** END OF THE TEST ***'

clean 0
