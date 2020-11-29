import Vue from 'vue'
import Vuetify, { VList } from 'vuetify/lib'
import colors from 'vuetify/lib/util/colors'

Vue.use(Vuetify, {
  components: {
    VList
  }
})

const opts = {
  theme: {
    dark: false,
    themes: {
      light: {
        background: colors.shades.white,
        primary: colors.grey.darken3,
        secondary: colors.grey.lighten3,
        accent: colors.shades.white,
        info: colors.blue,
        success: colors.green,
        error: colors.red.darken1
      },
      dark: {
        background: colors.grey.darken3,
        primary: colors.grey.darken4,
        secondary: '#363636',
        accent: colors.grey.darken4,
        info: colors.blue.darken3,
        success: colors.green.darken3,
        error: colors.red.darken4
      }
    },
    options: {
      customProperties: true
    },
  },
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
