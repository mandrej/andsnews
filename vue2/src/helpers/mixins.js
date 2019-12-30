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
       * If you want users to download anonymously accessible objects without authenticating,
       * use the storage.googleapis.com
       */
      if (!rec.repr_url) return '/static/img/broken.svg'
      let serviceUrl = '/api/thumb/' + rec.safekey + '/' + size
      const max = Math.max(...rec.dim)
      if (!size || size > max) {
        if (process.env.NODE_ENV === 'development') {
          serviceUrl = '/_ah/gcs' + rec.repr_url
        } else {
          serviceUrl = 'https://storage.cloud.google.com' + rec.repr_url
        }
      }
      return serviceUrl
    }
  }
}

export default common
