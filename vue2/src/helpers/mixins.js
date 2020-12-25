import CONFIG from './config'

const common = {
  data: () => ({
    requiredRule: [value => !!value || 'Required.']
  }),
  computed: {
    version () {
      const ver = process.env.VUE_APP_VERSION.match(/.{1,4}/g).join('.')
      return '© 2007 - ' + ver
    },
    noBack () {
      if (this.editForm) return true
      if (this.confirm) return true
      return false
    }
  },
  methods: {
    splitDate (dateTime) {
      if (dateTime) {
        const dt = dateTime.split(' ')
        return {
          date: dt[0],
          time: dt[1]
        }
      }
      return { date: '', time: '' }
    },
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
          serviceUrl = '/api/thumb/' + rec.filename + '?size=' + size
        } else {
          serviceUrl = CONFIG.google_storage_url + rec.filename
        }
      }
      return serviceUrl
    }
  },
  beforeRouteLeave (to, from, next) {
    // List -> close open popups instead of going back
    if (this.noBack) {
      this.editForm = false
      this.confirm = false
      next(false)
    } else {
      next()
    }
  }
}

export default common
