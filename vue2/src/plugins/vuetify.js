import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

Vue.use(Vuetify, {
  theme: {
    primary:    '#3F51B5', // indigo
    secondary:  '#536DFE', // indigo-accent-2,
    accent:     '#FFC107', // amber
    error:      '#FF1744', // red-accent-3,
    warning:    '#E0E0E0', // grey-lighten-2,
    info:       '#2196F3', // blue
    success:    '#4CAF50'  // green
  }
})
