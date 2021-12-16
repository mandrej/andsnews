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
        appbar: colors.shades.white,
        background: colors.grey.lighten3,
        primary: colors.teal,
        secondary: colors.teal,
        accent: colors.grey.lighten3
      },
      dark: {
        appbar: colors.grey.darken2,
        background: colors.grey.darken3,
        primary: colors.teal.darken1,
        secondary: colors.teal.accent3,
        accent: colors.grey.darken3
      }
    },
    options: {
      customProperties: true
    }
  },
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
