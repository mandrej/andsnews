<template>
  <v-app>
    <v-toolbar app dark class="aperture" color="error">
      <v-btn icon @click="$router.push({ name: 'home' })">
        <v-icon>home</v-icon>
      </v-btn>
      <v-toolbar-title class="headline">{{title}}</v-toolbar-title>
    </v-toolbar>

    <v-content>
      <v-container>
        <v-responsive height="200px">
          <v-container fill-height>
            <v-layout column justify-center align-center>
              <v-icon x-large color="seconadry">error</v-icon>
              <h3 class="title">{{text}}</h3>
            </v-layout>
          </v-container>
        </v-responsive>
      </v-container>
    </v-content>

    <Footer/>
  </v-app>
</template>

<script>
export default {
  name: 'Err',
  components: {
    'Footer': () => import(/* webpackChunkName: "footer" */ '@/components/Footer')
  },
  props: ['title', 'text']
}
</script>

<style lang="scss" scoped>
.v-responsive {
  outline: 2px dashed #BDBDBD;
  & h3 {
    padding-top: 1em;
    text-align: center;
  }
}
</style>
