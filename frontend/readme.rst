Javascript frontend for AppEnlight
===================================

To fetch all the requirememts you need to have nodejs and npm installed on your dev machine, then from this dir execute::

    npm install
    npm install -g bower
    npm install -g grunt-cli
    bower install

This will fetch all the required components to build front with grunt.


To build production version (builds both js and css) just run::

    grunt

To work on dev code version (builds js with comments and css) run:

    grunt watch

You generally shouldn't need to run those separately but still:

To work on just Javascript version with comments run:

    grunt watch:dev

To work on just CSS files run:

    grunt watch:css

Ubuntu/Debian and broken node - running from node_modules instead system ones
-----------------------------------------------------------------------------

Download this:

    http://nodejs.org/dist/v0.10.32/node-v0.10.32-linux-x64.tar.gz

unpack to your home into "node" directory then edit your .bashrc file to include:

export PATH=$PATH:~/node/bin

now you will be able to execute all the comands above just fine


