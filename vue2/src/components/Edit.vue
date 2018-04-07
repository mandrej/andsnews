<template>
  <div class="page-container">
    <md-app>
      <md-app-toolbar class="md-primary">
        <span class="md-title">Edit</span>
      </md-app-toolbar>

      <md-app-content>
        <md-button class="md-primary">Submit</md-button>
        <md-field>
          <label>Headline</label>
          <md-input v-model="rec.headline"></md-input>
        </md-field>
        <div class="md-layout md-gutter">
          <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-medium-size-33 md-size-33">
          </div>
        </div>
      </md-app-content>
    </md-app>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Edit',
  data () {
    return {
      rec: {}
    }
  },
  created () {
    this.$store.dispatch('getRecord', this.$route.params.id)
  },
  computed: {
    ...mapState(['current'])
  },
  watch: {
    current (newVal, oldVal) {
      if (!newVal) return
      this.createRecord(newVal)
    }
  },
  methods: {
    createRecord (obj) {
      this.rec = obj
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

</style>
