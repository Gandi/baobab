*/5 * * * *  www-data PYTHONPATH=/etc/ DJANGO_SETTINGS_MODULE=gandi.baobab /usr/bin/baobab twitter 2>&1| logger -t baobab
*/5 * * * *  www-data PYTHONPATH=/etc/ DJANGO_SETTINGS_MODULE=gandi.baobab /usr/bin/baobab close_event 2>&1| logger -t baobab
