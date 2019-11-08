import Vue from 'vue'
import Vuetify from 'vuetify/lib'

Vue.use(Vuetify)

const opts = {
  theme: {
    dark: false,
    themes: {
      light: {
        primary: '#455A64', // blue-grey darken-2
        secondary: '#37474f', // blue-grey darken-3
        accent: '#ffc107', // amber
        error: '#ff5252', // red accent-2
        warning: '#e0e0e0', // grey lighten-2
        info: '#2196f3', // blue
        success: '#4caf50' // green
      }
    }
  },
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
