import CONFIG from './config'
import firebase from 'firebase/app'
import 'firebase/messaging'

if (!firebase.apps.length) {
  firebase.initializeApp(CONFIG.firebase)
}
export default firebase.messaging()
