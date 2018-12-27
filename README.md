# README
* This is personal site for photos
* Built using Google App Engine and python 2.7

### Set up virtualenv
* Install python 2.7, virtualenv, pip and Google App Engine
* Create virtualenv, activate it and install requirements

### Google requirements
- Active GroundLink account on Google
- Create application on [Google Developers Console](https://console.developers.google.com/project)

### Firebase requirements
- Go to [Firebase Console](https://console.firebase.google.com) using same Google account 
- Choose application for firebase support
- Copy credentials for web app
- Pick menu Overview, Project settings, General, Cloud Messaging
- Copy Server key and Sender ID

### Client requirements
- Go to vue2/
- yarn install

### Deployment on Google infrastructure
* $> ./ands devel
* $> ./ands build (client)
* $> ./ands deploy api|client


### Linked libraries
/
- decorator.py -> /home/milan/venv/andsnews/lib/python2.7/site-packages/decorator.py
- six.py -> /home/milan/venv/andsnews/lib/python2.7/site-packages/six.py

/lib
click -> /home/milan/venv/andsnews/lib/python2.7/site-packages/click/
cloudstorage -> /home/milan/venv/andsnews/lib/python2.7/site-packages/cloudstorage/
exifread -> /home/milan/venv/andsnews/lib/python2.7/site-packages/exifread/
flask -> /home/milan/venv/andsnews/lib/python2.7/site-packages/flask/
httplib2 -> /home/milan/venv/andsnews/lib/python2.7/site-packages/httplib2
itsdangerous -> /home/milan/venv/andsnews/lib/python2.7/site-packages/itsdangerous
jinja2 -> /home/milan/venv/andsnews/lib/python2.7/site-packages/jinja2/
markupsafe -> /home/milan/venv/andsnews/lib/python2.7/site-packages/markupsafe/
unidecode -> /home/milan/venv/andsnews/lib/python2.7/site-packages/unidecode/
werkzeug -> /home/milan/venv/andsnews/lib/python2.7/site-packages/werkzeug/
