/* eslint-disable no-undef */
/* eslint-disable no-unused-vars */

import { initializeApp } from "firebase/app";
import { getMessaging } from "firebase/messaging/sw";

const firebaseApp = initializeApp({
  apiKey: "AIzaSyBj5uKo0P_mir_ChQ_syx_kUQ_g7nkNy6M",
  authDomain: "andsnews.firebaseapp.com",
  databaseURL: "https://andsnews.firebaseio.com",
  projectId: "andsnews",
  storageBucket: "andsnews.appspot.com",
  messagingSenderId: "719127177629",
  appId: "1:719127177629:web:5e1335058fa70551186774",
});
const messaging = getMessaging(firebaseApp);
