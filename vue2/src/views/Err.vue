<template>
  <div>
    <v-app>
      <v-toolbar app dark prominent color="error">
        <v-btn icon  @click="$router.push({name: 'home'})">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <v-toolbar-title class="headline">{{title}}</v-toolbar-title>
      </v-toolbar>

      <v-content>
        <v-container fluid>
          <v-jumbotron color="warning">
            <v-container fill-height>
              <v-layout column justify-center align-center>
                <v-icon x-large color="seconadry">error</v-icon>
                <h3 class="title">{{text}}</h3>
              </v-layout>
            </v-container>
          </v-jumbotron>
        </v-container>
      </v-content>

      <Footer/>
    </v-app>
  </div>
</template>

<script>
export default {
  name: 'Err',
  components: {
    'Footer': () => import('@/components/Footer'),
  },
  props: ['title', 'text']
}
</script>

<style lang="scss" scoped>
.v-jumbotron {
  height: 200px !important;
  & h3 {
    padding-top: 1em;
    text-align: center;
  }
}
</style>
