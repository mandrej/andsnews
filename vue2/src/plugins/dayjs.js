import Vue from 'vue'
import dayjs from 'dayjs'
// import 'dayjs/locale/sr-cyrl'
import localeData from 'dayjs/plugin/localeData'
dayjs.extend(localeData)
// dayjs.locale('sr-cyrl')

Object.defineProperties(Vue.prototype, {
  $date: {
    get () {
      return dayjs
    }
  }
})
