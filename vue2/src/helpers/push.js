import Vue from 'vue'
import CONFIG from '@/helpers/config'

const axios = Vue.axios

export default function (token, msg) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': 'key=' + CONFIG.fcm_server_key
  }
  const data = {
    to: token,
    notification: {
      title: 'ands',
      body: msg
    }
  }
  axios
    .post(CONFIG.fcm_send, data, { headers: headers })
    .then()
    .catch(() => console.error('push message failed'))
}
