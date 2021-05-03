import CONFIG from './config'
import firebase from 'firebase/app'

if (!firebase.apps.length) {
  firebase.initializeApp(CONFIG.firebase)
}
export default firebase
