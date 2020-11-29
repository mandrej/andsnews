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
        accent: colors.amber.lighten1,
        info: colors.blue,
        success: colors.green,
        error: colors.red.darken1
      },
      dark: {
        background: colors.grey.darken3,
        primary: colors.grey.darken4,
        secondary: colors.grey.darken2,
        accent: colors.red.darken4,
        info: colors.blue.darken2,
        success: colors.green.darken2,
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
