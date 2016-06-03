# appenlight README


To run the app you need to have meet prerequusites:

- running elasticsearch (2.2 tested)
- running postgresql 9.5
- running redis

# Setup basics

Set up the basic application database schema:

    appenlight_initialize_db config.ini

Set up basic elasticsearch schema:

    appenlight-reindex-elasticsearch -c config.ini -t all


# Running

To run the application itself:

    pserve --reload development.ini

To run celery queue processing:

    celery worker -A appenlight.celery -Q "reports,logs,metrics,default" --ini=development.ini


# Testing

To run test suite:

    py.test appenlight/tests/tests.py --cov appenlight (this looks for testing.ini in repo root)

WARNING!!!
Some tests will insert data into elasticsearch or redis based on testing.ini
