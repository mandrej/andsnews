<template>
  <v-container>
    <v-alert type="error" transition="scale-transition" prominent>{{
      text
    }}</v-alert>
  </v-container>
</template>

<script>
export default {
  name: 'Err',
  props: ['text']
}
</script>
