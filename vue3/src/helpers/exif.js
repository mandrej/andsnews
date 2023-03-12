import api from "./api";
import notify from "./notify";

export default function readExif(filename) {
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
}
