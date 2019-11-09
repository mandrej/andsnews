<template>
  <v-dialog v-model="dialogModel" max-width="300px" persistent>
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
  props: ['model', 'title', 'text'],
  computed: {
    dialogModel () {
      return this.model
    }
  }
}
</script>
