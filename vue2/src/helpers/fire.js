import CONFIG from './config'
import { initializeApp } from 'firebase/app'

export default initializeApp(CONFIG.firebase)
