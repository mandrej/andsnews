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
        background: colors.grey.lighten3,
        primary: colors.shades.white,
        secondary: colors.shades.white,
        accent: colors.teal.accent3,
        info: colors.teal,
        success: colors.teal,
        error: colors.red.accent2
      },
      dark: {
        background: colors.grey.darken3,
        primary: colors.grey.darken4,
        secondary: colors.grey.darken2,
        accent: colors.teal.accent4,
        info: colors.teal,
        success: colors.teal.darken2,
        error: colors.red.accent4
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
