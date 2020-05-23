import CONFIG from './config'
import firebase from 'firebase/app'

export default firebase.initializeApp(CONFIG.firebase)
