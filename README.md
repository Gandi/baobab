# Gandi Baobab

The application that powers Gandi's Status website ([status.gandi.net](https://status.gandi.net)).

## OVERVIEW

Baobab is a Python and web application divided into 3 parts:
 - a Django-powered back-end (`./baobab/backoffice` and `./baobab/translate`)
 - a REST API (`./baobab/apirest`)
 - a web client that uses the REST API (`./baobab.front`)

It has 5 app namespaces that allow you to work (test, migrate, etc.) on specific parts: `backoffice`, `apirest`, `rss`, `translate` and `socialnetwork`.

Baobab requires a database and supports SQLite, PostgreSQL or MySQL. 

Node.js and npm are required to build the web client app.

Cron jobs are used to publish Tweets and close events on a schedule.

## DEVELOPMENT

### INSTALLATION

Clone the repository and enter the local directory that was just created.

We recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/) to manage local python environments.

    $ virtualenv /some/directory/virtual
    $ source /some/directory/virtual/bin/activate
    $ python setup.py install

A `$ baobab` command should be available after install. Otherwise, please try to use it from the installation directory:
  
    $ cd /some/directory/virtual/lib/python2.7/dist-packages/baobab/bin
    $ ./cmd_baobab.py <...>
  
This can be caused by an error in `django-tastypie`'s `setup.py` distributed in the Debian package.

**Note for Gnome users**: A "baobab" command can already exist in your system (Disk Usage Analyzer), so make sure you use virtualenv as recommended.

### APPLICATION SETTINGS

The settings file is located in `./baobab/settings.py`. **Make sure you edit this file to setup your installation**.

In it, you can define some default data such user and admin accounts, as well as important options such as the `SECRET_KEY`, default time zones or to change `DEBUG=False` when not in development.

For production (actually, whenever `DEBUG is not True`) you need to authorize your hosts by editing `ALLOWED_HOSTS = []`.

More information on Django settings can be found [in the docs](https://docs.djangoproject.com/en/1.4/ref/settings).

#### Using a custom settings file

For example, create a Python package at `/etc/baobab/__init__.py` and your settings module file at `/etc/baobab/settings.py`.

You can make sure your package will be in your Python's path by exporting it

    $ export PYTHONPATH=/etc
    
Then you can use the `--settings` flag, like so:

    $ baobab <command> --settings baobab.settings
    
Alternatively, you can set Django's buit-in environment variable

    $ export DJANGO_SETTINGS_MODULE=baobab.settings
    $ baobab <command>

### BUILD THE WEB CLIENT

Install the web client's dependencies and build the app

    $ npm install
    $ npm run dev

### SETUP THE DATABASE

Load the schema and create the default data

    $ baobab setup-dev

By default, a SQLite database file will be created at `./baobab/default.db` if it doesn't exist.

### LAUNCH THE SERVER

To launch the web server with the admin interface and REST API :

    $ baobab runserver

Or  `$ ./baobab/bin/cmd_baobab.py runserver` if you've built the debian package.

Open your browser at `http://localhost:8000/` to see the website. The admin page is accessible at `http://localhost:8000/admin`.

### API USAGE

In addition to the web client, Baobab is also usable via a REST API that delivers content in JSON format. 

The API is self-described, so you can start exploring it by making a simple request to the main endpoint.

Example:

    $ curl http://localhost:8000/api | python -m json.tools

    {
        "events": {
            "list_endpoint": "/api/events",
            "schema": "/api/events/schema"
        },
        "services": {
            "list_endpoint": "/api/services",
            "schema": "/api/services/schema"
        },
        "status": {
            "list_endpoint": "/api/status",
            "schema": "/api/status/schema"
        }
    }


### UPDATING THE DATABASE MODEL

Follow this simple process to modify the database structure. Migrations are managed with [South](http://south.aeracode.org/).

1. Modify the application's models
2. Create schema migration files
3. Create data migration files if necessary
4. Apply the migrations

#### Changing the model

Update `models.py` in the appropriate app folder to add / remove fields and/or tables (for example `./baobab/backoffice/models.py`).

#### Creating a schema migration

    $ baobab schemamigration <namespace> --auto

**Tip**: Remember to use `db.rename_column` in a migration script to rename a field.

#### Creating a data migration 

    $ baobab datamigration <namespace> <data_migration_name>

#### Running migrations

    $ baobab migrate  

**Tip**: when switching branches, you might forget to rollback or apply relevant migrations. You can avoid that by adding a git hook. See some examples in`./misc/hooks/*`.

### OVERRIDING THE DEFAULT USER

You can override the default user login credentials by setting the `DEFAULT_USER_LOGIN` and `DEFAULT_USER_PASSWORD` variables.

If these variables are not set when the setup scripts are run, you will be prompted to create a default user.

### Social network integrations: Twitter, IRC, etc.

#### Custom integrations

At the moment baobab can publish status updates to Twitter and IRC, but you can easily add your own integrations.
You only need to create a new class in the `socialnetwork` app and inherit from the `SocialNetworkBase` class.

Each social network has its own configuration. Please take a look at the `settings.py` file for more information.

Upon the creation of an `Event`, a status update will be immediately published to each configured integration.

#### Maintenance

When the event is of the `Maintenance` type, baobab can publish a status update automatically at the estimated start date.
Simply create a cron task to execute `$ baobad social_network` to achieve this.

### TRANSLATIONS
 
You can easily translate content published with Baobab and retrieve translated content via the API.

Special user permissions can be granted for translators, and the translation interface is available in the backoffice at http://localhost:8000/admin/translate.`

You can then retrieve translated content by adding the "Accept-Language" header to your API requests. If you don't, Baobab automatically falls back to English (the default language).

For example:

    curl -H "Accept-Language: fr" http://localhost:8000/api/events

Please note that while the web client can consume translated content (browsers will automatically send the `Accept-Language` header according to the user's language), the web interface itself is not localised (nor localisable in the current state of the implementation).

### TESTING

You can run unit tests on specific namespaces or the whole app. No configuration is necessary for this.

    $ baobab test <namespace>

Note the `translate` namespace has no dedicated testing suite. The translation features are tested within the `apirest` namespace.

## PRODUCTION USAGE

In a production environment, you'll want to use different settings and technologies to better serve your app securily at scale.

We use Gunicorn as the app server, along with Nginx to proxy HTTP requests, instead of just running Django's webserver.

An example Gunicorn config for Baobab could look like this:

```
CONFIG = {
    'working_dir': '/srv/baobab',
    'environment': {
        'DJANGO_SETTINGS_MODULE': 'myown.settings',
        'PYTHONPATH': '/etc/'
    },
    'args': (
        '--bind=127.0.0.1:8008',
        '--workers=4',
        '--timeout=10',
        'baobab.wsgi:application',
    ),
}

```

Your production-ready settings file would then reside in `/etc/myown/settings.py`, along with the Python package file `/etc/myown/__init__.py`.

Also check the `nginx/sites-available/` folder for our sample Nginx configuration files.

You could also use MySQL or PostgreSQL as database backends instead of SQLite, for example.

### Manual deploy

After copying the application files to the server, install the web client's dependencies and build it for release (repeat whenever these assets change)

    $ npm install
    $ NODE_ENV=production npm run release

Then, setup the database and run migrations (repeat whenever the model changes)

    $ baobab syncdb
    
Now you can start or restart your chosen webserver solution.

### Debian package

Baobab can also be built into a Debian package, which is useful for production deployments on compatible systems. Gandi's own packaging details can be found in the `debian/` folder.

To build the package:

    $ debuild -us -uc -b || dpkg-buildpackage -us -uc -b

You can then place it on a Production server and install it. All scripts will be automatically launched. You can then start or restart the app and web servers.

## CONTRIBUTING

### Create issues

Any major changes should be documented as [a GitHub issue](#) before you start working on it.

### Proposing your changes

Don't hesitate -- we appreciate every contribution, no matter how small.

Create a git branch with your new feature or bugfix and either (in order of preference):

* open a Pull Request on GitHub
* mail the patch to feedback@gandi.net,
* send the URL for your branch and we will review/merge it if correct

We'll check your pull requests in the timeliest manner possible. If we can't accept your PR for some reason,
we'll give you feedback and you're encouraged to try again!

### Submission conventions

Fork the repository and make changes on your fork in a feature branch:

- If it's a bug fix branch, name it XXXX-something where XXXX is the number of the issue.
- If it's a feature branch, create an enhancement issue to announce your intentions, and name it XXXX-something where XXXX is the number of the issue.

#### Tests

Submit unit tests for your changes. Run the full test suite on your branch before submitting a pull request.

#### Documentation

Update the documentation when creating or modifying features.

## Code status

[![Build Status](https://travis-ci.org/Gandi/baobab.svg?branch=master)](https://travis-ci.org/Gandi/baobab)
[![Coverage Status](https://coveralls.io/repos/Gandi/baobab/badge.svg?branch=master)](https://coveralls.io/r/Gandi/baobab?branch=master)

## LICENSE

Please see the `LICENSE` file.