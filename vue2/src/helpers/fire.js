import firebase from 'firebase/app'
import 'firebase/app'

const config = {
  apiKey: 'AIzaSyBj5uKo0P_mir_ChQ_syx_kUQ_g7nkNy6M',
  authDomain: 'andsnews.firebaseapp.com',
  databaseURL: 'https://andsnews.firebaseio.com',
  projectId: 'andsnews',
  storageBucket: 'andsnews.appspot.com',
  messagingSenderId: '719127177629'
}
export const FB = firebase.initializeApp(config)

// messaging.usePublicVapidKey('BEMvPS8oRWveXcM6M_uBdQvDFZqvYKUOnUa22hVvMMlSMFr_04rI3G3BjJWW7EZKSqkM2mchPP3tReV4LY0Y45o')
// export const MESSAGING_AUTH = {
//   'Content-Type': 'application/json',
//   'Authorization': 'key=AAAAp29R6Z0:APA91bEsmfN6-ZywxP05Xpw-Ooto5FwTyXjgxRcqDllaTo6Kay3y8wnB-1QcwBt1-iQvoPt2p8wwp0JmKz4xWHST-pAQyrAivyTT-RFXasRYGmT09rP6oMuW95XHEi-HANZgzljuA-4i4Gh44den43zooddq5uSjBA',
//   'project_id': config.messagingSenderId
// }
