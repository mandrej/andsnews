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
        primary: colors.blue.darken4,
        secondary: colors.lime.darken1,
        accent: colors.orange.lighten3
      }
    }
  },
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
