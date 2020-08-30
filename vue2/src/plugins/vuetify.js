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
        primary: colors.grey.darken3,
        secondary: colors.grey.lighten2,
        accent: colors.shades.white,
        info: colors.blue,
        success: colors.green,
        error: colors.red.darken1
      },
      dark: {
        primary: colors.shades.black,
        secondary: colors.grey.daken4,
        accent: colors.shades.black,
        info: colors.blue.darken3,
        success: colors.green.darken3,
        error: colors.red.darken4
      }
    }
  },
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
