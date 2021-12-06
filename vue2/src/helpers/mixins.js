import CONFIG from './config'

const common = {
  data: () => ({
    requiredRule: [value => !!value || 'Required.']
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
    },
    getImgSrc (rec, size) {
      /**
       * Enter allUsers in Add Members. Then Select Role > Storage > Storage Object Viewer
       */
      let serviceUrl = CONFIG.fileBroken
      if (rec.filename !== null) {
        if (size) {
          serviceUrl = CONFIG.smallsized_storage_url + rec.filename
        } else {
          serviceUrl = CONFIG.fullsized_storage_url + rec.filename
        }
      }
      return serviceUrl
    }
  }
}

export default common
