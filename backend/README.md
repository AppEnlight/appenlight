AppEnlight
-----------

Performance, exception, and uptime monitoring for the Web

![AppEnlight image](https://raw.githubusercontent.com/AppEnlight/appenlight/gh-pages/static/appenlight.png)

Automatic Installation
======================

Use the ansible scripts in the `automation` repository to build complete instance of application
You can also use `packer` files in `automation/packer` to create whole VM's for KVM and VMWare.

Manual Installation
===================

To run the app you need to have meet prerequsites:

- python 3.5+ (currently 3.6 tested)
- running elasticsearch (6.6.2 tested)
- running postgresql (9.5+ required, tested 9.6 and 10.6)
- running redis

Install the app by performing

    pip install -r requirements.txt
    
    python setup.py develop

Install the appenlight uptime plugin (`ae_uptime_ce` package from `appenlight-uptime-ce` repository).

For production usage you can do:

    pip install appenlight
    pip install ae_uptime_ce


After installing the application you need to perform following steps:

1. (optional) generate production.ini (or use a copy of development.ini)

        appenlight-make-config production.ini

2. Setup database structure:

       appenlight-migratedb -c FILENAME.ini

3. To configure elasticsearch:

       appenlight-reindex-elasticsearch -t all -c FILENAME.ini

4. Create base database objects 

   (run this command with help flag to see how to create administrator user)

       appenlight-initializedb -c FILENAME.ini

5. Generate static assets

       appenlight-static -c FILENAME.ini

Running application
===================

To run the main app:

    pserve development.ini

To run celery workers:

    celery worker -A appenlight.celery -Q "reports,logs,metrics,default" --ini FILENAME.ini

To run celery beat:

    celery beat -A appenlight.celery --ini FILENAME.ini

To run appenlight's uptime plugin:

    appenlight-uptime-monitor -c FILENAME.ini

Real-time Notifications
=======================

You should also run the `channelstream websocket server for real-time notifications

    channelstream -i filename.ini

Additional documentation
========================

Visit  https://getappenlight.com for additional server and client documentation.

Testing
=======

To run test suite:

    py.test appenlight/tests/tests.py --cov appenlight (this looks for testing.ini in repo root)


Development
===========

To develop appenlight frontend:

    cd frontend
    npm install
    grunt watch

