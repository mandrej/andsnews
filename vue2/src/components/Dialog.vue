<template>
  <v-dialog :value="model" max-width="300px" :persistent="persistent">
    <v-card>
      <v-card-title class="headline" primary-title>{{title}}</v-card-title>
      <v-card-text>{{text}}</v-card-text>
      <v-divider></v-divider>
      <v-card-actions class="px-8 py-4">
        <slot></slot>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'Dialog',
  props: {
    model: {
      type: Boolean,
      default: false,
      required: true
    }, persistent: {
      type: Boolean,
      default: false,
    }, title: {
      type: String,
      default: 'TITLE'
    }, text: {
      type: String,
      default: 'TEXT'
    }
  }
}
</script>
