# README
* This is personal site for photos
* Built using Google App Engine and python 3.7

### Set up virtualenv
* Install python 3.7, virtualenv, pip and Google App Engine SDK
* Create virtualenv, activate it and install requirements

### Google requirements
- Active Google account
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
* $> ./ands build
* $> ./ands deploy
