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
        primary: colors.blueGrey,
        secondary: colors.blueGrey.lighten3,
        accent: colors.orange.lighten2,
        info: colors.blue,
        success: colors.green,
        error: colors.red.darken2
      },
      dark: {
        primary: colors.teal,
        secondary: colors.teal.darken3,
        accent: colors.brown,
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
