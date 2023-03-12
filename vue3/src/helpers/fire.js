import { CONFIG } from "./index";
import { initializeApp } from "firebase/app";

const firebaseApp = initializeApp(CONFIG.firebase);
export default firebaseApp;
