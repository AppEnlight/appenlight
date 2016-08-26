
One place to keep all RhodeCode documentation projects.

Code is **automatically** picked up by our CI server and all documentation will
be built and published on:

    https://docs.rhodecode.com/RhodeCode-Appenlight


Quickstart
==========

Get the code via::

    hg clone https://code.rhodecode.com/appenlight-docs
    cd appenlight-docs

Build all::

    make all

Build a project (eg. Internal-docs)::

    make Internal-docs

or::

    make help 

to find which make options are available.



FAQ
===

1. In which format I have to write?
   
   Learn how to use Sphinx and get comfortable with RestructuredText.

   http://sphinx-doc.org/contents.html

2. My changes are not visible?

   Wait 5min to be sure CI server had enough time to pickup your changes.

   If still not showing, make sure you've added your file to Sphinx's
   ``toctree``
