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
      // size: '400-c'
      const suffix = size ? '=s' + size : '=s0'
      if (rec && rec.repr_url) {
        if (process.env.NODE_ENV === 'development') {
          return '/_ah/gcs' + rec.repr_url + '?' + suffix
        } else {
          return 'https://storage.googleapis.com' + rec.repr_url + '?' + suffix
        }
      } else {
        return '/static/img/broken.svg'
      }
    }
  }
}

export default common
