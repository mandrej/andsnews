# README

- This is personal site for photos
- Built using Google App Engine and python 3.8

### Set up virtualenv

- Install python 3.8, virtualenv, pip and Google App Engine SDK
- Create virtualenv, activate it and install requirements

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

- Go to vue3/
- yarn install

### Google Cloud storage

#### make public access

> Bucket, Edit bucket premission, ADD MEMBER:

> allusers: Storage Object Viewer

#### add cache-control

```bash
$> export BUCKET=andsnews.appspot.com
$> gsutil -m setmeta -h "Cache-Control:public, max-age=86400" gs://$BUCKET/*.jpg
```

### Deployment on Google infrastructure

```bash
$> ./ands devel
$> ./ands icons
$> ./ands build
$> ./ands serve
$> ./ands deploy
```
