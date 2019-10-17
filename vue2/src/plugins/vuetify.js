import Vue from 'vue'
import Vuetify from 'vuetify/lib'

Vue.use(Vuetify)

const opts = {
  theme: {
    dark: false,
    themes: {
      light: {
        primary: '#BDBDBD', // grey lighten-1
        secondary: '#37474F', // blue-grey darken-3
        accent: '#FFC107', // amber
        error: '#FF1744', // red-accent-3,
        warning: '#E0E0E0', // grey-lighten-2
        info: '#2196F3', // blue
        success: '#4CAF50' // green
      }
    }
  },
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
