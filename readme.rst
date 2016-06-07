App Enlight
-----------

Automatic Installation
======================

Use the ansible scripts in the `/automation` directory to build complete instance of application
You can also use `packer` files in `/automation/packer` to create whole VM's for KVM and VMWare.

Manual Installation
===================

Install the app by performing

    pip install -r requirements.txt
    
    python setup.py develop

To run the app and configure datastore you need to run:

* elasticsearch (2.2+ tested)
* postgresql 9.5+
* redis 2.8+

after installing the application you need to:

1. (optional) generate production.ini (or use a copy of development.ini)

    appenlight-make-config production.ini

2. setup database structure:

    appenlight-migrate-db -c FILENAME.ini

3. to configure elasticsearch:

    appenlight-reindex-elasticsearch -c FILENAME.ini

4. create base database objects

    appenlight-initializedb -c FILENAME.ini

5. generate static assets

    appenlight-static -c FILENAME.ini

Running application
===================

to run the main app:

    pserve development.ini

to run celery workers:

    celery worker -A appenlight.celery -Q "reports,logs,metrics,default" --ini FILENAME.ini

to run celery beat:

    celery beat -A appenlight.celery --ini FILENAME.ini

to run appenlight's uptime plugin:

    appenlight-uptime-monitor -c FILENAME.ini
