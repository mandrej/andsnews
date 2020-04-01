<template>
  <v-container my-10>
    <h1>{{title}}</h1>
    <v-alert type="error" transition="scale-transition" prominent>{{text}}</v-alert>
  </v-container>
</template>

<script>
export default {
  name: 'Err',
  props: ['title', 'text']
}
</script>
