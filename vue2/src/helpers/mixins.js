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
    getImgSrc (rec, size) {
      // size: '400-c'
      const suffix = (size) ? '=s' + size : '=s0'
      if (rec && rec.serving_url) {
        if (process.env.NODE_ENV === 'development') {
          return rec.serving_url.replace('http://localhost:6060/_ah', '/_ah') + suffix
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
