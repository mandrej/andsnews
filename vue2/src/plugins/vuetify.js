import Vue from 'vue'
import Vuetify from 'vuetify/lib'

Vue.use(Vuetify)

const opts = {
  theme: {
    dark: false,
    themes: {
      light: {
        primary: '#bdbdbd', // grey lighten-1
        secondary: '#37474f', // blue-grey darken-3
        accent: '#ffc107', // amber
        error: '#ff1744', // red-accent-3,
        warning: '#e0e0e0', // grey-lighten-2
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
