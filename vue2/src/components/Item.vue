<template>
  <v-dialog
    v-model="show"
    fullscreen
    transition="dialog-bottom-transition"
    :overlay="false"
    scrollable>
    <v-card tile>
      <v-toolbar card dark color="primary">
        <v-btn icon @click.native="show = false">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>{{rec.headline || title}}</v-toolbar-title>
        <v-spacer></v-spacer>
        <!-- <v-btn @click="submit" :disabled="!valid" light>Submit</v-btn> -->
      </v-toolbar>
      <v-card-text>
         <img :src="src(rec)" :alt="rec.slug">
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'Item',
  props: ['visible', 'rec'],
  data: () => ({
    title: 'Not found'
  }),
  computed: {
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
    src (rec) {
      if (rec && rec.serving_url) {
        if (process.env.NODE_ENV === 'development') {
          return rec.serving_url.replace('http://localhost:8080/_ah', '/_ah') + '=s0'
        } else {
          return rec.serving_url + '=s0'
        }
      } else {
        return '/static/broken.svg'
      }
    }
  }
}
</script>

<style lang="scss" scoped>
img {
  width: 100%;
}
</style>
