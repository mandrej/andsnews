import Vue from 'vue'
import dayjs from 'dayjs'
// import 'dayjs/locale/sr-cyrl'
// dayjs.locale('sr-cyrl')
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

Object.defineProperties(Vue.prototype, {
  $date: {
    get () {
      return dayjs
    }
  }
})
