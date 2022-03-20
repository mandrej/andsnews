import CONFIG from "../../../config.json";
import { Notify } from "quasar";
import axios from "axios";
import { initializeApp } from "firebase/app";
import { date, format } from "quasar";

const api = axios.create({ baseURL: "/api", timeout: 60000 }); // 60 sec
const firebase = initializeApp(CONFIG.firebase);
const { humanStorageSize } = format;
const { formatDate } = date;

const notify = (options) => {
  /**
   * type: 'positive', 'negative', 'warning', 'info', 'ongoing', 'external'
   */
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment
  let { type, message, timeout, spinner, group, position } = options;
  if (
    message.startsWith(CONFIG.start_message) ||
    message.startsWith(CONFIG.end_message)
  ) {
    timeout = 0;
    spinner = true;
  }
  Notify.create({
    type: type ? type : "info",
    message: message,
    timeout: timeout ? timeout : 5000,
    spinner: spinner ? true : false,
    group: group ? group : false,
    position: position ? position : "bottom",
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
const months = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];
const formatBytes = (bytes, decimals = 2) => {
  return humanStorageSize(bytes);
};
const formatDatum = (str, format) => {
  const date = new Date(str);
  return formatDate(date, format);
};
const readExif = (filename) => {
  return new Promise((resolve, reject) => {
    api
      .get("exif/" + filename)
      .then((response) => {
        resolve(response.data);
      })
      .catch((err) => {
        reject(err);
        notify({
          type: "negative",
          message: err,
        });
      });
  });
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
  months,
  formatBytes,
  formatDatum,
  readExif,
};
