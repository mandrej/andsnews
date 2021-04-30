import Vue from 'vue'

const axios = Vue.axios

export default function (token, msg) {
  axios
    .post('message/send', {
      message: msg
    })
    .then()
    .catch(() => console.error('push message failed'))
}
