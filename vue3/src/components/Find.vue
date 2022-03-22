<template>
  <div class="q-pa-md q-gutter-md">
    <q-input
      v-model="tmp.text"
      :disable="busy"
      @keyup.enter="submit"
      label="by text"
      clearIcon="clear"
      clearable
    />
    <Complete
      :modelValue="tmp.tags"
      :options="values.tags"
      multiple
      label="by tags"
      :disable="busy"
      @update:model-value="newValue => { tmp.tags = newValue; submit() }"
    />
    <Complete
      class="col"
      :modelValue="tmp.year"
      :options="optionsYear"
      autocomplete="label"
      label="by year"
      :disable="busy"
      @update:model-value="newValue => { tmp.year = newValue; submit() }"
    />
    <div class="row">
      <Complete
        class="col"
        :modelValue="tmp.month"
        :options="optionsMonth"
        autocomplete="label"
        label="by month"
        :disable="busy"
        @update:model-value="newValue => { tmp.month = newValue; submit() }"
      />
      <div class="col-1"></div>
      <Complete
        class="col"
        :modelValue="tmp.day"
        :options="optionsDay"
        autocomplete="label"
        label="by day"
        :disable="busy"
        @update:model-value="newValue => { tmp.day = newValue; submit() }"
      />
    </div>
    <Complete
      :modelValue="tmp.model"
      :options="values.model"
      label="by model"
      :disable="busy"
      @update:model-value="newValue => { tmp.model = newValue; submit() }"
    />
    <Complete
      :modelValue="tmp.lens"
      :options="values.lens"
      label="by lens"
      :disable="busy"
      @update:model-value="newValue => { tmp.lens = newValue; submit() }"
    />
    <Complete
      :modelValue="tmp.nick"
      :options="nickNames"
      label="by author"
      :disable="busy"
      @update:model-value="newValue => { tmp.nick = newValue; submit() }"
    />
  </div>
</template>

<script setup>
import { onMounted, computed, watch, ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useStore } from "vuex";
import Complete from "./Complete.vue";
import { months } from "../helpers";

const store = useStore();
const route = useRoute();
const router = useRouter();
const busy = computed(() => store.state.app.busy)
const values = computed(() => store.state.app.values)
const nickNames = computed(() => store.getters["app/nickNames"])

const find = computed(() => store.state.app.find)
const tmp = ref(find.value)

const queryDispatch = (query) => {
  // delete keys without values
  Object.keys(query).forEach((key) => {
    if (tmp.value[key] == null) {
      delete tmp.value[key];
    }
  });
  // adopt to match types
  Object.keys(tmp.value).forEach((key) => {
    if (["year", "month", "day"].includes(key)) {
      tmp.value[key] = +query[key];;
    } else if (key === "tags") {
      if (typeof tmp.value[key] === "string" || tmp.value[key] instanceof String) {
        tmp.value[key] = [query[key]];
      }
    }
  });
  const strFind = JSON.stringify(find.value)
  const strTmp = JSON.stringify(tmp.value)
  if (strFind !== strTmp) {
    store.commit("app/saveFindForm", tmp.value);
    // new query
    store.commit("app/setBusy", false); // interupt loading
    store.dispatch("app/fetchRecords", true); // new filter with reset
    // this dispatch route change
    if (Object.keys(tmp.value).length) {
      if (route.hash) {
        router.push({ path: "/list", query: tmp.value, hash: route.hash });
      } else {
        router.push({ path: "/list", query: tmp.value });
      }
    } else if (route.name === 'list') {
      router.push({ path: "/" });
    }
  }
}

// front router-link, hash detailed carousel
onMounted(() => {
  if (route.name !== 'list') return
  tmp.value = { ...route.query }
  queryDispatch(route.query)
  // console.log('onMounted ', tmp.value);
})

// back from carousel
watch(route, (to) => setForm(to), { deep: true });
const setForm = (to) => {
  if (to.name !== 'list') return
  tmp.value = { ...to.query }
  queryDispatch(to.query)
  // console.log('watch route ', tmp.value);
}

const submit = () => {
  queryDispatch(tmp.value)
  // console.log('submit ', tmp.value);
}

const optionsYear = computed(() => {
  return values.value.year.map(year => {
    return { label: '' + year, value: year }
  })
})
const optionsMonth = computed(() => {
  return months.map((month, i) => ({ label: month, value: i + 1 }));
})
const optionsDay = computed(() => {
  const N = 31,
    from = 1,
    step = 1;
  return [...Array(N)].map((_, i) => from + i * step).map(day => {
    return { label: '' + day, value: day }
  });
})
</script>
