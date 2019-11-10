const common = {
  data: () => ({
    requiredRule: [value => !!value || 'Required.']
  }),
  methods: {
    updateSnackbar (val) {
      // <Message :model="snackbar" :message="message" @update-snackbar="updateSnackbar"></Message>
      this.snackbar = val
    },
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
    }
  }
}

export default common
