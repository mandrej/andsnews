import Vue from 'vue'
import Vuetify from 'vuetify/lib/framework'

Vue.use(Vuetify)

const opts = {
  theme: {
    dark: false,
    themes: {
      light: {
        card: '#ffffff',
        drawer: '#ffffff',
        background: '#eeeeee',
        primary: '#07a0ab',
        secondary: '#ffbd66',
        error: '#da2525'
      },
      dark: {
        card: '#383838',
        drawer: '#555555',
        background: '#424242',
        primary: '#05737a',
        secondary: '#ffab40',
        error: '#c42121'
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
