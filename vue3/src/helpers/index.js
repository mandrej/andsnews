import CONFIG from "../../../config.json"
import { Notify } from "quasar";
import axios from "axios";
import { initializeApp } from "firebase/app";

const api = axios.create({ baseURL: "/api", timeout: 60000 }); // 1 min
const firebase = initializeApp(CONFIG.firebase);

const notify = function (type, message) {
  /**
   * type: 'positive', 'negative', 'warning', 'info', 'ongoing'
   */
  Notify.create({
    type: type,
    // color: "positive",
    timeout: 2000,
    position: "bottom-left",
    message: message,
  });
};
const pushMessage = function (recipients, msg) {
  api
    .post("message/send", {
      recipients: recipients,
      message: msg,
    })
    .then()
    .catch(() => console.error("push message failed"));
};

const fileBroken = CONFIG.fileBroken;
const fullsized = CONFIG.public_url + "fullsized/";
const smallsized = CONFIG.public_url + "smallsized/";
const formatBytes = function (bytes, decimals = 2) {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
};

export {
  CONFIG,
  api,
  firebase,
  notify,
  pushMessage,
  fileBroken,
  fullsized,
  smallsized,
  formatBytes,
};
