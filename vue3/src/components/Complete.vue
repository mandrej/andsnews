<template>
  <q-select
    v-if="autocomplete"
    :disable="disable"
    v-model="modelRef"
    :options="optionsRef"
    use-input
    clearable
    fill-input
    hide-selected
    emit-value
    map-options
    input-debounce="0"
    @filter="filter"
    :label="label"
    @input="$emit('update:model', $event.target.value)"
  />
  <q-select
    v-else
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
  model: {
    type: [String, Number],
    required: false
  },
  options: Array,
  label: String,
  autocomplete: {
    type: String,
    requered: false
  },
  disable: {
    type: Boolean,
    default: false
  },
})
const emit = defineEmits(['update:model'])

const modelRef = ref(props.model)
const optionsRef = ref(props.options)
const field = props.autocomplete // label

function filter(val, update) {
  console.log(val);
  if (val === '') {
    update(() => {
      optionsRef.value = props.options
    })
    return
  }
  update(() => {
    const needle = val.toLowerCase()
    if (field) {
      optionsRef.value = props.options.filter(v => v[field].toLowerCase().indexOf(needle) > -1)
    } else {
      optionsRef.value = props.options.filter(v => v.toLowerCase().indexOf(needle) > -1)
    }
  })
}

</script>


