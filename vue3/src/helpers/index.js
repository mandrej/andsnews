import CONFIG from "../../../config.json";
import { date, format } from "quasar";

const { humanStorageSize } = format;
const { formatDate } = date;

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
const emailNick = (email) => {
  return email.match(/[^.@]+/)[0];
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

export const U = "_";
export const fileBroken = CONFIG.fileBroken;
export const fullsized = CONFIG.public_url + "andsnews.appspot.com/";
export const smallsized = CONFIG.public_url + "thumbnails400/";
export {
  CONFIG,
  months,
  formatBytes,
  formatDatum,
  emailNick,
  fakeHistory,
  removeHash,
};
