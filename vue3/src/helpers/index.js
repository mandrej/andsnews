import CONFIG from "../../../config.json";
import { Notify } from "quasar";
import axios from "axios";
import { initializeApp } from "firebase/app";
import { date, format } from "quasar";

const api = axios.create({ baseURL: "/api", timeout: 60000 }); // GAE timeout 60 sec
const firebase = initializeApp(CONFIG.firebase);
const { humanStorageSize } = format;
const { formatDate } = date;

const notify = (options) => {
  /**
   * type: 'positive', 'negative', 'warning', 'info', 'ongoing', 'external'
   */
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment
  let { type, message, multiLine, timeout, spinner, group, position } = options;
  if (!message) return;
  if (
    message.startsWith(CONFIG.start_message) ||
    message.startsWith(CONFIG.end_message)
  ) {
    timeout = 0;
  }
  Notify.create({
    type: type ? type : "info",
    message: message,
    multiLine: multiLine ? true : false,
    timeout: timeout ? timeout : 5000,
    spinner: spinner ? true : false,
    group: group ? group : false,
    position: position ? position : "bottom",
    textColor: "white",
    actions: [{ icon: "close", color: "white" }],
  });
};
const pushMessage = (recipients, msg) => {
  api
    .post(
      "message/send",
      {
        recipients: recipients,
        message: msg,
      },
      { timeout: 0 }
    )
    .then((resp) => {
      /**
       * on message send: pushMessage  2 successfully sent, 1 failed
       * recalc bycket: pushMessage  projects/andsnews/messages/dbc730ff-9e70-4f37-b907-50644f489565 sent
       */
      if (process.env.DEV) console.log("pushMessage ", resp.data);
    })
    .catch((err) => {
      console.error(err);
      notify({ type: "negative", message: "Push message failed" });
    });
};

const fileBroken = CONFIG.fileBroken;
const fullsized = CONFIG.public_url + "andsnews.appspot.com/";
const smallsized = CONFIG.public_url + "thumbnails400/";
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
// eslint-disable-next-line no-unused-vars
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
        notify({ type: "negative", message: err.message });
      });
  });
};
const emailNick = (email) => {
  return email.match(/[^.@]+/)[0];
};
const U = "_";
const cardAttributes = (filename) => {
  const [name, ext] = filename.split(".");
  return {
    id: U + name,
    class: ext + " bg-grey-2",
  };
};
const fakeHistory = () => {
  window.history.pushState(history.state, null, history.state.current);
};
const removeHash = () => {
  window.history.replaceState(
    history.state,
    null,
    history.state.current.replace(/#(.*)?/, "")
  );
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
  emailNick,
  U,
  cardAttributes,
  fakeHistory,
  removeHash,
};
