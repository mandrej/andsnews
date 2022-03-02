<template>
  <!-- <Taging
    :model="tmp.tags"
    :options="values.tags"
    @done="submit()"
    label="by tag"
    :disable="busy"
  />-->
  <q-select
    :disable="disable"
    v-model="modelRef"
    :options="optionsRef"
    use-input
    hide-selected
    fill-input
    input-debounce="0"
    @filter="filter"
    @update:model-value="emit('done', modelRef.value)"
    label="by tag"
    clearable
  >
    <!-- <template v-slot:append>
      <q-icon
        v-if="modelRef.value && modelRef.value.length !== 0"
        class="cursor-pointer"
        name="clear"
        @click.stop="modelRef.value = []; emit('done', modelRef.value)"
      />
    </template>-->
  </q-select>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  model: Array,
  options: Array,
  label: String,
  disable: Boolean,
})
const emit = defineEmits(['done'])

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
function setModel(val) {
  // @update:model-value="submit"
  console.log(modelRef.value);
  emit('done', modelRef.value)
}

</script>


