const common = {
  data: () => ({
    requiredRule: [
      v => !!v || 'Required Field'
    ]
  }),
  computed: {
    // v-dialog v-model="show"
    show: {
      get () {
        return this.visible
      },
      set (value) {
        if (!value) {
          this.$emit('close')
        }
      }
    }
  },
  methods: {
    linearize (dict) {
      let params = []
      const sep = '"' // because of tags:b&w -> tags:"b&w"

      function wrap (key, value) {
        if (key === 'text') {
          params.push(sep + value.toLowerCase() + sep)
        } else {
          params.push(key + ':' + sep + value + sep)
        }
      }
      Object.keys(dict).forEach(key => {
        if (key === 'tags') {
          dict[key].forEach(tag => {
            wrap(key, tag)
          })
        } else {
          if (dict[key]) {
            wrap(key, dict[key])
          }
        }
      })
      return params.join(' AND ')
    },
    formatDate (iso) {
      return iso.replace('T', ' ').substring(0, 16)
    },
    getImgSrc (rec, size) {
      // size: '400-c'
      const suffix = (size) ? '=s' + size : '=s0'
      if (rec && rec.serving_url) {
        // 'http://localhost:8080/_ah/gcs' + rec.filename
        // 'https://storage.googleapis.com' + rec.filename // needs access rights
        if (process.env.NODE_ENV === 'development') {
          return rec.serving_url.replace('http://localhost:6060/_ah', '/_ah') + suffix
        } else {
          return rec.serving_url + suffix
        }
      } else {
        return '/static/img/broken.svg'
      }
    },
    getName (email) {
      return email.match(/[^@]+/)[0].split('.')[0]
    }
  }
}

export default common
