# Nosferatu

Nosferatu is a webapp for home automation written in python3 (Flask) and coffeescript (angular).

The app is used to control the status of various local devices over WiFi. Any recognized device can be turned on/off and otherwise controlled manually or though the use of rules and schedules that control when and why they change state.

----

## Quick Start
```bash
# The commands to install Nosferatu's dependencies are as follows:
sudo apt-get install build-essential python3-dev libpq-dev libffi-dev postgresql postgresql-contrib coffeescript ruby
sudo gem install sass

# Create the virtual environment and activate it
virtualenv --no-site-packages --distribute .
source bin/activate

# To install the app you can run:
python setup.py install
createdb nosferatu                       # Creates the database.
mkdir -p var/nosferatu-instance          # Creates the local settings path
touch var/nosferatu-instance/config.py   # and file.
# Inside this file you can put any local overrides to configuration for the app.
# This includes the following two *required* pieces of configuration.
#     SECRET_KEY = 'some-secret-key-here!'
#     SQLALCHEMY_DATABASE_URI = 'postgresql:///nosferatu

# You should be able to upgrade the database to the most recent version through running
python manage.py db upgrade

# Finally run the server by calling (and then navigating to `127.0.0.1:5000`)
python manage.py runserver
```
