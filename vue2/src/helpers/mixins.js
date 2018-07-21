const common = {
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
  methods:{
    getImgSrc (rec, size) {
      const suffix = (size) ? '=s400-c' : '=s0'
      if (rec && rec.serving_url) {
        if (process.env.NODE_ENV === 'development') {
          return rec.serving_url.replace('http://localhost:6060/_ah', '/_ah') + suffix
        } else {
          return rec.serving_url + suffix
        }
      } else {
        return '/static/img/broken.svg'
      }
    },
    dateFormat (rec, fmt) {
      if (rec && rec.date) {
        let [date, time] = rec.date.split('T')
        let [year, month, day] = date.split('-')
        if (fmt) {
          return [day, month, year].join('.')
        } else {
          return [day, month, year].join('.') + ' ' + time
        }
      }
    }
  }
}

export default common
