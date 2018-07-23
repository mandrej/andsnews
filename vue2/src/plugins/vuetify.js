import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

Vue.use(Vuetify, {
  theme: {
    primary:    '#BDBDBD', // grey lighten-1
    secondary:  '#616161', // grey darken-2
    accent:     '#FFC107', // amber
    error:      '#FF1744', // red-accent-3,
    warning:    '#E0E0E0', // grey-lighten-2
    info:       '#2196F3', // blue
    success:    '#4CAF50'  // green
  }
})
