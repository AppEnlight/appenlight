Application Monitoring
======================

You can connect multiple applications to |RAE| for monitoring. To do this,
use the information in this section.

Adding an Application
---------------------

1. Select :menuselection:`Settings --> Create Application`.
2. Set the :guilabel:`Application name` and :guilabel:`Application URL`.
3. Click :guilabel:`Create Application`.

.. note::

    You will need to configure your application to communicate with |RAE|.
    See the instructions for your particular framework in the
    `Appenlight Developer Docs`_.

Transfer Application Ownership
------------------------------

1. Select :menuselection:`Admin --> List Applications --> Settings`
2. In the :guilabel:`Transfer Ownership` section, enter the following
   details:

    - The current owner's password
    - The new owner's username

3. Click :guilabel:`Transfer Ownership of application`

Adding Users and User Groups
----------------------------

Access to each application is granted on a :guilabel:`User Group` or
:guilabel:`User` basis, see the :ref:`user-perms` section for more details.

Removing an Application
-----------------------

To remove an application from |RAE|, us the following steps.

1. Select :menuselection:`Admin --> List Applications`
2. Click :guilabel:`Settings` beside the application you want to delete.
3. Click :guilabel:`Delete my application`


.. _Appenlight Developer Docs: https://appenlight.rhodecode.com/page/api/main
