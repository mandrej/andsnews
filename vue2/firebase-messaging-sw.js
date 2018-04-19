// Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('/node_modules/firebase/firebase-app.js');
importScripts('/node_modules/firebase/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in the
// messagingSenderId.
firebase.initializeApp({
    'messagingSenderId': '719127177629'
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
messaging.usePublicVapidKey('BEMvPS8oRWveXcM6M_uBdQvDFZqvYKUOnUa22hVvMMlSMFr_04rI3G3BjJWW7EZKSqkM2mchPP3tReV4LY0Y45o')
