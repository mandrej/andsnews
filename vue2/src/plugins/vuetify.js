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
        secondary: colors.grey.lighten4,
        accent: colors.teal.accent3,
        info: colors.teal,
        success: colors.teal,
        error: colors.red.accent2
      },
      dark: {
        background: colors.grey.darken4,
        primary: colors.grey.darken3,
        secondary: '#333',
        accent: colors.teal.darken2,
        info: colors.teal.darken2,
        success: colors.teal.darken3,
        error: colors.red.darken3
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
