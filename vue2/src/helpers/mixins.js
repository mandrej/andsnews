const common = {
  data: () => ({
    drawerKey: 0,
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
      // size: '400-c'
      const suffix = size ? '=s' + size : '=s0'
      if (rec && rec.serving_url) {
        // 'http://localhost:8080/_ah/gcs' + rec.filename
        // 'https://storage.googleapis.com' + rec.filename // needs access rights
        if (process.env.NODE_ENV === 'development') {
          return (
            rec.serving_url.replace('http://localhost:6060/_ah', '/_ah') +
            suffix
          )
        } else {
          return rec.serving_url + suffix
        }
      } else {
        return '/static/img/broken.svg'
      }
    },
    redrawDrawer () {
      this.drawerKey++
    }
  }
}

export default common
