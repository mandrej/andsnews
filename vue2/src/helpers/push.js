import Vue from 'vue'

const axios = Vue.axios

export default function (recipients, msg) {
  axios
    .post('message/send', {
      recipients: recipients,
      message: msg
    })
    .then()
    .catch(() => console.error('push message failed'))
}
