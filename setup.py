import os
from setuptools import setup

def read(fname):
    return

setup(
    name = 'Nosferatu',
    version = '0.4.4',
    author = 'Daniel Cardin',
    author_email = 'ddcardin@gmail.com',
    description = (
        'A webapp to remotely control your home lights and wall sockets'
    ),
    license = 'Apache 2.0',
    keywords = 'nosferatu webapp home automation lights lightswitch',
    packages=['nosferatu', 'tests'],
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'APScheduler',
        'alembic',
        'cssmin',
        'Flask',
        'Flask-Assets',
        'Flask-User',
        'Flask-Cache',
        'Flask-Login',
        'Flask-Migrate',
        'Flask-SQLAlchemy',
        'SQLAlchemy',
        'gunicorn',
        'jsmin',
        'psycopg2',
        'redis',
        'webassets',
    ],
)
