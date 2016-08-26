.. _install-ova:

Installation Using An OVA
=========================

|RAE| is currently only available as an OVA(Open Virtualization Archive) for
installation on virtual machines. To obtain this file, contact
support@rhodecode.com.

The OVA is packaged using VMWare 8.0, so it would be better to use the same
version. You can use a different VMWare version but you will need to use
their copatibility option,
:menuselection:`virtual machine --> settings --> copatibility`

Installation Steps
------------------

To install |RAE| using an OVA and VMWare, use the following steps.

1. Contact |RC| to get the latest OVA file.
2. Create a VMWare virtual machine using the OVA.
3. Sign into the VM with the *User/Password* combination provided.

    - The OVA is an Ubuntu based VM and |RAE| will be automatically running.
    - |RAE| will be served on https://rhodecode-appenlight.local.

4. To view your instance of |RAE| you will need to make changes
   to your local machine's hosts file to resolve the IP Address of the VM.

   From the VM, use the ``ifconfig`` command to display the local network
   settings and note the IP Address.

.. code-block:: bash

    # Display your network details.
    $ ifconfig -a

5. On your local machine, update the hosts file to resolve the IP Address
   when you access the |RAE| URL: https://rhodecode-appenlight.local

   Where `192.0.2.0` is changed to your VMs IP Address.

.. code-block:: bash

    # Appenlight VM IP Address
    192.0.2.0   rhodecode-appenlight.local

Once running you can connect |RAE| and |RCE|. See the
:ref:`connect-enterprise` section.
