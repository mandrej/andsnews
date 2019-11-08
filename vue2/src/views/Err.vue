<template>
  <v-app>
    <v-app-bar app light>
      <v-btn icon @click="$router.push({ name: 'home' })">
        <v-icon>home</v-icon>
      </v-btn>
      <v-img src="/static/img/aperture.svg" max-height="40" max-width="40" class="mr-3"></v-img>
      <v-toolbar-title class="headline">{{title}}</v-toolbar-title>
    </v-app-bar>

    <v-content>
      <v-container mt-4>
        <div class="dotted mb-3 pa-4">
          <v-layout column justify-center align-center style="height: 120px">
            <h3 class="headline">{{text}}</h3>
          </v-layout>
        </div>
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
