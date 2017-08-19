# README #

### What is this repository for? ###

* This is personal site for photos and blog
* Built using Google App Engine and python 2.7
* Current version 1511

### How do I get set up? ###

* Install python 2.7, virtualenv, pip and Google App Engine
* Create virtualenv, activate it and install requirements
* In virtualenv lib folder clone [aeta](https://code.google.com/p/aeta/)
* Symlink all libraries to project lib:
    * cloudstorage, colormath, exifread, googleapiclient,
    * pyasn1, pyasn1_modules, rsa,
    * httplib2, networkx, oauth2client

### Deployment instructions ###

* Create application on [Google Developers Console](https://console.developers.google.com/project)
* cd client/
* $> bower install / update
* $> npm install / update
* $> cd ..
* $> ./ands devel
* $> ./ands build
* $> ./ands deploy to Deploy on Google infrastructure
