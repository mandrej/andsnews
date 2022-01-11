import CONFIG from './config'
import {
  mdiArrowUp,
  mdiCrosshairsGps,
  mdiDelete,
  mdiPencil,
  mdiDownload,
  mdiClose,
  mdiCalendar,
  mdiClockOutline,
  mdiAccountCircle,
  mdiPlusCircle,
  mdiCog,
  mdiPalette
} from '@mdi/js'

const common = {
  data: () => ({
    requiredRule: [(value) => !!value || 'Required.'],
    fileBroken: CONFIG.fileBroken,
    fullsized: CONFIG.public_url + 'fullsized/',
    smallsized: CONFIG.public_url + 'smallsized/',
    // icons //
    mdiArrowUp: mdiArrowUp,
    mdiCrosshairsGps: mdiCrosshairsGps,
    mdiDelete: mdiDelete,
    mdiPencil: mdiPencil,
    mdiDownload: mdiDownload,
    mdiClose: mdiClose,
    mdiCalendar: mdiCalendar,
    mdiClockOutline: mdiClockOutline,
    mdiAccountCircle: mdiAccountCircle,
    mdiPlusCircle: mdiPlusCircle,
    mdiCog: mdiCog,
    mdiPalette: mdiPalette
  }),
  computed: {
    version () {
      const ver = process.env.VUE_APP_VERSION.match(/.{1,4}/g).join('.')
      return '© 2007 - ' + ver
    }
  },
  methods: {
    formatBytes (bytes, decimals = 2) {
      if (bytes === 0) return '0 Bytes'

      const k = 1024
      const dm = decimals < 0 ? 0 : decimals
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))

      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
    }
  }
}

export default common
