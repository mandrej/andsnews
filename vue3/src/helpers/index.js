import CONFIG from "../../../config.json";
import { Notify } from "quasar";
import axios from "axios";
import { initializeApp } from "firebase/app";
import { date, format } from "quasar";

const api = axios.create({ baseURL: "/api", timeout: 60000 }); // 1 min
const firebase = initializeApp(CONFIG.firebase);
const { humanStorageSize } = format;
const { extractDate, formatDate } = date;

const d = new Date("2022-02-12 16:33");
console.log(d, formatDate(d, "DD MMM YYYY HH:mm"));

Notify.registerType("external", {
  color: "grey-8",
});

const notify = (type, message, timeout = 5000) => {
  /**
   * type: 'positive', 'negative', 'warning', 'info', 'ongoing', 'external'
   */
  if (message.startsWith(CONFIG.end_message)) {
    timeout = 0;
  }
  Notify.create({
    type: type,
    timeout: timeout,
    position: "bottom",
    message: message,
    textColor: "white",
    actions: [{ icon: "close", color: "white" }],
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
const formatBytes = (bytes, decimals = 2) => {
  return humanStorageSize(bytes);
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
