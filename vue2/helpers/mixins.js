import moment from 'moment'

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
          return rec.serving_url.replace('http://localhost:8080/_ah', '/_ah') + suffix
        } else {
          return rec.serving_url + suffix
        }
      } else {
        return '/static/broken.svg'
      }
    },
    dateFormat (str, fmt) {
      if (!fmt) fmt = 'llll'
      return moment(str, 'YYYY-MM-DDTHH:mm:ss').format(fmt)
    }
  }
}

export default common
