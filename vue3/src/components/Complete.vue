<template>
  <q-select
    :disable="disable"
    v-model="modelRef"
    :options="optionsRef"
    use-input
    clearable
    fill-input
    hide-selected
    input-debounce="0"
    @filter="filter"
    :label="label"
    @input="$emit('update:model', $event.target.value)"
  />
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  model: String,
  options: Array,
  label: String,
  disable: {
    type: Boolean,
    default: false
  },
})
const emit = defineEmits(['update:model'])

const modelRef = ref(props.model)
const optionsRef = ref(props.options)

function filter(val, update) {
  if (val === '') {
    update(() => {
      optionsRef.value = props.options
    })
    return
  }
  update(() => {
    const needle = val.toLowerCase()
    optionsRef.value = props.options.filter(v => v.toLowerCase().indexOf(needle) > -1)
  })
}

</script>


