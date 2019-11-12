<template>
  <v-app>
    <v-app-bar app light>
      <v-btn icon @click="$router.push({ name: 'home' })">
        <v-icon>home</v-icon>
      </v-btn>
      <v-img src="/static/img/aperture.svg" max-height="40" max-width="40" class="mr-3"></v-img>
      <v-toolbar-title class="headline">{{title}}</v-toolbar-title>
    </v-app-bar>

    <v-content class="accent">
      <v-container my-10>
        <v-alert type="error" transition="scale-transition" prominent dark>{{text}}</v-alert>
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
