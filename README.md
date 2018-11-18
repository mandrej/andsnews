# README
* This is personal site for photos
* Built using Google App Engine and python 2.7

### Set up virtualenv
* Install python 2.7, virtualenv, pip and Google App Engine
* Create virtualenv, activate it and install requirements
* In virtualenv lib folder clone [aeta](https://code.google.com/p/aeta/)
* Symlink all libraries to project lib:
    * aeta, cloudstorage, colormath, exifread, googleapiclient,
    * pyasn1, pyasn1_modules, rsa,
    * httplib2, networkx, oauth2client

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
- Go to p2/
- bower install/ update

### Deployment on Google infrastructure
* $> ./ands devel
* $> ./ands build
* $> ./ands deploy


### Linked libraries
/
- decorator.py -> /home/milan/venv/andsnews/lib/python2.7/site-packages/decorator.py
- six.py -> /home/milan/venv/andsnews/lib/python2.7/site-packages/six.py

/lib
aeta -> /home/milan/venv/andsnews/lib/aeta/aeta/
cloudstorage -> /home/milan/venv/andsnews/lib/python2.7/site-packages/cloudstorage/
colormath -> /home/milan/venv/andsnews/lib/python2.7/site-packages/colormath
exifread -> /home/milan/venv/andsnews/lib/python2.7/site-packages/exifread/
httplib2 -> /home/milan/venv/andsnews/lib/python2.7/site-packages/httplib2
networkx -> /home/milan/venv/andsnews/lib/python2.7/site-packages/networkx
numpy -> /home/milan/venv/andsnews/lib/python2.7/site-packages/numpy
pytz -> /home/milan/venv/andsnews/lib/python2.7/site-packages/pytz
unidecode -> /home/milan/venv/andsnews/lib/python2.7/site-packages/unidecode/
