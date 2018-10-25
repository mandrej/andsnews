<template>
  <v-snackbar
      v-model="tmpModel"
      :timeout="timeout"
      left
      bottom>
      {{ text }}
      <v-btn flat icon color="white" @click="tmpModel = false">
        <v-icon>close</v-icon>
      </v-btn>
    </v-snackbar>
</template>

<script>
export default {
  name: 'SanckBar',
  props: {
    model: {
      type: Boolean,
      default: false
    },
    text: {
      type: String,
      required: true
    },
    timeout: {
      type: Number,
      default: 6000
    }
  },
  // data: () => ({
  //   tmpModel: this.model
  // }),
  computed: {
    tmpModel: {
      get () {
        return this.model
      },
      set (value) {
        // if (!value) {
        //   this.$emit('close')
        // }
      }
    }
  }
}
</script>
