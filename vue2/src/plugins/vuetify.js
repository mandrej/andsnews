import Vue from 'vue'
import Vuetify, { VList } from 'vuetify/lib'
import 'vuetify/src/stylus/app.styl'

Vue.use(Vuetify, {
  components: {
    VList
  },
  theme: {
    primary: '#BDBDBD', // grey lighten-1
    secondary: '#37474F', // blue-grey darken-3
    accent: '#FFC107', // amber
    error: '#FF1744', // red-accent-3,
    warning: '#E0E0E0', // grey-lighten-2
    info: '#2196F3', // blue
    success: '#4CAF50' // green
  }
})
