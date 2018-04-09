<template>
  <div class="page-container">
    <md-app>
      <md-app-toolbar class="md-primary">
        <span class="md-title">Edit</span>
      </md-app-toolbar>

      <md-app-content>
        <form @submit.prevent="checkForm">
          <md-button type="submit" class="md-primary">Submit</md-button>
          <md-field>
            <label>Headline for {{rec.filename}}</label>
            <md-input v-model="rec.headline" required></md-input>
          </md-field>

          <md-chips v-model="rec.tags" md-placeholder="Add tag..."></md-chips>

          <div class="md-layout md-gutter">
            <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-size-33">
              <md-autocomplete v-model="rec.author" :md-options="authors" required>
                <label>Author</label>
              </md-autocomplete>
            </div>
            <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-size-33">
              <md-field>
                <label>Date taken</label>
                <md-input v-model="rec.date"></md-input>
              </md-field>
            </div>
            <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-size-33">
              <md-field>
                <label>Camera Model</label>
                <md-input v-model="rec.model"></md-input>
              </md-field>
            </div>
            <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-size-33">
              <md-field>
                <label>Lens</label>
                <md-input v-model="rec.lens"></md-input>
              </md-field>
            </div>
            <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-size-33">
              <md-field>
                <label>Focal length</label>
                <md-input type="number" v-model="rec.focal_length"></md-input>
              </md-field>
            </div>
            <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-size-33">
              <md-field>
                <label>ISO [ASA]</label>
                <md-input type="number" v-model="rec.iso"></md-input>
              </md-field>
            </div>
            <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-size-33">
              <md-field>
                <label>Aperture</label>
                <md-input type="number" step="0.1" v-model="rec.aperture"></md-input>
              </md-field>
            </div>
            <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-size-33">
              <md-field>
                <label>Shutter [s]</label>
                <md-input v-model="rec.shutter"></md-input>
              </md-field>
            </div>
            <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-size-33">
              <md-field>
                <label>Color</label>
                <md-input v-model="rec.color" disabled></md-input>
              </md-field>
            </div>
          </div>
        </form>
      </md-app-content>
    </md-app>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Edit',
  data: () => ({
    rec: {},
    authors: [
      'milan.andrejevic@gmail.com',
      'mihailo.genije@gmail.com',
      'svetlana.andrejevic@gmail.com',
      'ana.devic@gmail.com',
      'dannytaboo@gmail.com',
      'zile.zikson@gmail.com'
    ]
  }),
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
    },
    checkForm (e) {
      // console.log(e.target.elements)
      this.$store.dispatch('saveRecord', this.rec.safekey)
      const {back} = this.$route.meta
      this.$router.replace({name: back})
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

</style>
