# Nosferatu

Nosferatu is a webapp for home automation written in python3 (Flask) and coffeescript (angular).

The app is used to control the status of various local devices over WiFi. Any recognized device can be turned on/off and otherwise controlled manually or though the use of rules and schedules that control when and why they change state.

----

## Quick Start

    # The commands to install Nosferatu's dependencies are as follows:
    sudo apt-get install build-essential python3-dev libpq-dev libffi-dev postgresql postgresql-contrib coffeescript ruby
    sudo gem install sass

    # postgres should be used to create a database and a local `config.py` through something like...
    sudo -u postgres createdb nosferatu

    # now your local settings file should be created like so...
    mkdir -p var/nosferatu-instance
    touch var/nosferatu-instance/config.py

    # Inside this file you can put any local overrides to configuration for the app.
    # This includes the following two required pieces of configuration.
    #     SECRET_KEY = 'some-secret-key-here!'
    #     SQLALCHEMY_DATABASE_URI = 'postgresql:///nameOfDatabase' # if you used the command above, it would be `nosferatu`!

    # Create the virtual environment
    virtualenv --no-site-packages --distribute .

    # Activate the virtualenv
    source bin/activate

    # To install the app you can run.
    python setup.py install

    # You should be able to upgrade the database to the most recent version through running
    python manage.py db upgrade

    # Finally run the server by calling (and then navigating to `127.0.0.1:5000`)
    python manage.py runserver
