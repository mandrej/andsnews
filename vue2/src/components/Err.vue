<template>
  <div>
    <v-app light>
      <v-toolbar app>
        <v-icon @click="$router.push({name: 'home'})">arrow_back</v-icon>
        <v-toolbar-title class="headline">{{title}}</v-toolbar-title>
      </v-toolbar>

      <v-content>
        <v-jumbotron color="grey lighten-2">
          <v-container fill-height>
            <v-layout column justify-center align-center>
              <v-icon x-large color="seconadry">error</v-icon>
              <h3 class="title">{{text}}</h3>
            </v-layout>
          </v-container>
        </v-jumbotron>
      </v-content>
    </v-app>
  </div>
</template>

<script>
export default {
  name: 'Err',
  props: ['title', 'text']
}
</script>

<style lang="scss" scoped>
.jumbotron {
  height: 200px !important;
  & h3 {
    padding-top: 1em;
    text-align: center;
  }
}
</style>
