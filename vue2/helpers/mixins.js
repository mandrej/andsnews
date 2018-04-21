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
    }
  }
};
export default common;
