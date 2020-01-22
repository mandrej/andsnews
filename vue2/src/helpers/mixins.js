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
    formatDate (iso) {
      return iso.replace('T', ' ').substring(0, 16)
    },
    getImgSrc (rec, size) {
      /**
       * Enter allUsers in Add Members. Then Select Role > Storage > Storage Object Viewer
       */
      let serviceUrl = '/static/img/broken.svg'
      if (rec.filename !== null) {
        if (size) {
          serviceUrl = '/api/thumb/' + rec.filename + '?size=' + size
        } else {
          serviceUrl = CONFIG.google_storage_url + rec.filename
        }
      }
      return serviceUrl
    }
  }
}

export default common
