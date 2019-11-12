import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import colors from 'vuetify/lib/util/colors'

Vue.use(Vuetify)

const opts = {
  theme: {
    dark: false,
    themes: {
      light: {
        primary: colors.teal.lighten1,
        secondary: colors.grey.lighten1,
        accent: colors.orange.lighten3,
        error: colors.red.lighten1,
        warning: colors.orange.lighten3,
        info: colors.blue.lighten1,
        success: colors.lighten2
      }
    }
  },
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
