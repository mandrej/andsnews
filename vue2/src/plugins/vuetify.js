import Vue from 'vue'
import Vuetify, { VList } from 'vuetify/lib/framework'

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
        card: '#FFFFFF',
        drawer: '#FFFFFF',
        background: '#EEEEEE',
        primary: '#045B62',
        secondary: '#FFAB40',
        error: '#A71C1C'
      },
      dark: {
        card: '#383838',
        drawer: '#555555',
        background: '#424242',
        primary: '#045B62',
        secondary: '#FFAB40',
        error: '#A71C1C'
      }
    },
    options: {
      customProperties: true
    }
  },
  icons: {
    iconfont: 'mdiSvg'
  }
}

export default new Vuetify(opts)
