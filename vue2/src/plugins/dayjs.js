import Vue from 'vue'
import dayjs from 'dayjs'
// import 'dayjs/locale/sr-cyrl'
// dayjs.locale('sr-cyrl')

Object.defineProperties(Vue.prototype, {
  $date: {
    get () {
      return dayjs
    }
  }
})
