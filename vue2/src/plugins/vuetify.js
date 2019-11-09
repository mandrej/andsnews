import Vue from 'vue'
import Vuetify from 'vuetify/lib'

Vue.use(Vuetify)

const opts = {
  theme: {
    dark: false,
    themes: {
      light: {
        primary: '#424242', // grey darken-3
        secondary: '#bdbdbd', // grey lighten-1
        accent: '#ffc107', // amber
        error: '#ff1744', // red accent-3
        warning: '#e0e0e0', // grey lighten-2
        info: '#2979ff', // blue accent-3
        success: '#4caf50' // green
      }
    }
  },
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
