import Vue from 'vue'
import dayjs from 'dayjs'
// import 'dayjs/locale/sr-cyrl'
import localeData from 'dayjs/plugin/localeData'
import updateLocale from 'dayjs/plugin/updateLocale'
dayjs.extend(localeData)
dayjs.extend(updateLocale)
dayjs.updateLocale('en', {
  monthsShort: [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'
  ]
})
// dayjs.locale('sr-cyrl')

Object.defineProperties(Vue.prototype, {
  $date: {
    get () {
      return dayjs
    }
  }
})
