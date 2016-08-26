.. _rae-cli:

|RAE| CLI Guide
===============

appenlight-cleanup
------------------

.. py:function:: appenlight_cleanup [-c, --config <PATH>] [-t, --types <choices>]
    [-r, --resource <resource-id>] [-n, --namespace <resource-id>]

    Clean up the |RAE| database records.

    :argument -c --config: Location of the :file:`appenlight.ini` file.
    :argument -t --types: (Optional) Specify the records you want to cleanup in
      the database from the following options. The default value is ``logs``.

    :argument -r --resource: Specify which application's records you with to
        clean up. The *<resource-id>* refers to your application ID number,
        which you can get from the |RAE| interface.

    :argument -n --namespace: (Optional) Specify which namespace records you
        wish to clean up. You can check the available namespace records in
        your logs.


.. code-block:: bash

    # Clean up logs on resource ID 18
    $ ~/python/bin/appenlight_cleanup -c ~/appenlight/production.ini -t logs -r 18

appenlight-initializedb
-----------------------

.. py:function:: appenlight-initializedb <ini-file-name>

    Initialize |RAE| database.

    :argument -c --config: Location of the :file:`appenlight.ini` file.
    :argument --username: (Optional) Specify the username of the
        new administrator account.
    :argument --password: Specify the password of the administrator account.
    :argument --email: Specify the email of the administrator account.
    :argument --auth-token: Specify the auth token for the administrator.

.. code-block:: bash

    # Create a new dev.ini file and database
    $ ~/python/bin/appenlight-initializedb -c dev.ini

appenlight-migratedb
--------------------

.. py:function:: appenlight_migratedb <ini-file-name>

    Migrate the database associated with the specified :file:`.ini` file.

.. code-block:: bash

    # Migrate the specified DB
    $ ~/python/bin/appenlight-initializedb -c ~/appenlight/production.ini

appenlight-reindex-elastic-search
---------------------------------

.. py:function:: appenlight_reindex-elastic-search [-c, --config <PATH>] [-t, --types <choices>]

    :argument -c --config: Location of the :file:`appenlight.ini` file.
    :argument -t --types: (Optional) Specify the records you want to reindex in
      the database from the following options. The default value is to
      reindex all records.

      - ``reports``
      - ``logs``
      - ``metrics``
      - ``slow_calls``
      - ``template``
      - **other types inherited from plugins**

.. code-block:: bash

    # Reindex reports
    $ ~/python/bin/appenlight_reindex_elasticsearch -c ~/appenlight/production.ini -t reports

    # Reindex everything
    $ ~/python/bin/appenlight_reindex_elasticsearch -c ~/appenlight/production.ini

appenlight-uptime-monitor
-------------------------

.. py:function:: appenlight-uptime-monitor [-c, --config <PATH>] [-s, --sync-url <URL>]
    [-u, --update-url <URL>] [-l, --location <ping-id>] [-k, --api-key <api-key>]

    |RAE| Uptime Monitor.

    :argument -c --config: Location of the :file:`appenlight.ini` file.
    :argument -s --sync-url: Specify the source URL for monitoring. The
        default url is ``http://127.0.0.1:6543/api/uptime_app_list``.
    :argument -u --update-url: Specify the destination URL for the uptime
        data. The default value is ``http://127.0.0.1:6543/api/uptime``.
    :argument -l --location: Integer identifier for location of ping service.
        The default location is ``1``.
    :argument -k --api-key: The administrator user auth TOKEN.

.. code-block:: bash

    # Run uptime monitoring script
    $ ~/python/bin/appenlight-uptime-monitor -c uptime_config.ini
