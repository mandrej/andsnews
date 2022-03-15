<template>
  <q-select
    :disable="disable"
    v-model="model"
    :options="options"
    use-input
    clearable
    clearIcon="clear"
    :hide-selected="multiple ? false : true"
    :multiple="multiple ? true : undefined"
    :fill-input="multiple ? false : true"
    :emit-value="autocomplete ? true : undefined"
    :map-options="autocomplete ? true : undefined"
    :hide-dropdown-icon="canadd ? true : undefined"
    :new-value-mode="canadd ? 'add-unique' : undefined"
    :input-debounce="debounce"
    @filter="filter"
    :label="label"
    @input="$emit('update:model', $event.target.value)"
  />
</template>

<script setup>
import { ref } from "vue";

const emit = defineEmits(['update:model'])
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
    type: String, // 'label'
    default: ''
  },
  disable: {
    type: Boolean,
    default: false
  },
  label: String,
})

const model = ref(props.model)
const options = ref(props.options)
const field = props.autocomplete // label
const debounce = 300

function filter(val, update) {
  if (val === '') {
    update(() => {
      options.value = props.options
    })
    return
  }
  update(() => {
    const needle = val.toLowerCase()
    if (field) {
      options.value = props.options.filter(v => v[field].toLowerCase().indexOf(needle) > -1)
    } else {
      options.value = props.options.filter(v => v.toLowerCase().indexOf(needle) > -1)
    }
  })
}
</script>
