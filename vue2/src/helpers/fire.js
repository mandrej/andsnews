import CONFIG from './config'
import firebase from 'firebase/app'

let app = undefined
if (!firebase.apps.length) {
  app = firebase.initializeApp(CONFIG.firebase)
} else {
  app = firebase.app()
}
export default app
