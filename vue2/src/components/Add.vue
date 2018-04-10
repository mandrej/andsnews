<template>
  <div class="page-container">
    <md-app>
      <md-app-toolbar class="md-primary">
        <span class="md-title">Add</span>
      </md-app-toolbar>

      <md-app-content>
        <md-field>
          <label>Upload images</label>
          <md-file v-model="multiple" @change="processFiles" multiple accept="image/*" />
        </md-field>
      </md-app-content>
    </md-app>
  </div>
</template>

<script>

export default {
  name: 'Add',
  data: () => ({
    multiple: null
  }),
  methods: {
    processFiles (e) {
      // console.log(e.target.files)
      this.$store.dispatch('uploadList', e.target.files)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

</style>
