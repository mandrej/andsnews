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
    input-debounce="300"
    @filter="filter"
    :label="label"
    @input="$emit('update:model', $event.target.value)"
  />
  <q-select
    v-else-if="multiple"
    :disable="disable"
    v-model="modelRef"
    :options="optionsRef"
    multiple
    use-input
    clearable
    :hide-dropdown-icon="canadd ? true : null"
    :new-value-mode="canadd ? 'add-unique' : null"
    input-debounce="300"
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
    input-debounce="300"
    @filter="filter"
    :label="label"
    @input="$emit('update:model', $event.target.value)"
  />
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  model: {
    type: [String, Number, Array],
    required: false
  },
  options: Array,
  // tagging
  multiple: {
    type: Boolean,
    default: false
  },
  canadd: {
    type: Boolean,
    default: false,
  },
  // label and value
  autocomplete: {
    type: String,
    requered: false
  },
  disable: {
    type: Boolean,
    default: false
  },
  label: String,
})
const emit = defineEmits(['update:model'])

const modelRef = ref(props.model)
const optionsRef = ref(props.options)
const field = props.autocomplete // label

function filter(val, update) {
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


