<template>
  <v-app>
    <v-toolbar app flat light class="aperture">
      <v-btn icon @click="$router.push({ name: 'home' })">
        <v-icon>home</v-icon>
      </v-btn>
      <v-toolbar-title class="headline">{{title}}</v-toolbar-title>
    </v-toolbar>

    <v-content class="aperture">
      <v-container>
        <v-responsive height="200px">
          <v-container fill-height>
            <v-layout column justify-center align-center>
              <v-icon x-large>error</v-icon>
              <h3 class="title">{{text}}</h3>
            </v-layout>
          </v-container>
        </v-responsive>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
export default {
  name: 'Err',
  props: ['title', 'text']
}
</script>

<style lang="scss" scoped>
.v-responsive {
  outline: 2px dashed #37474F;
  & h3 {
    padding-top: 1em;
    text-align: center;
  }
}
</style>
