<template>
  <div class="q-pa-md q-gutter-md">
    <q-input v-model="tmp.text" :disable="busy" @keyup.enter="submit" label="by text" clearable />
    <Complete
      :model="tmp.tags"
      :options="values.tags"
      multiple
      label="by tags"
      :disable="busy"
      @update:model-value="newValue => { tmp.tags = newValue; submit() }"
    />
    <Complete
      class="col"
      :model="tmp.year"
      :options="optionsYear"
      autocomplete="label"
      label="by year"
      :disable="busy"
      @update:model-value="newValue => { tmp.year = newValue; submit() }"
    />
    <div class="row">
      <Complete
        class="col"
        :model="tmp.month"
        :options="optionsMonth"
        autocomplete="label"
        label="by month"
        :disable="busy"
        @update:model-value="newValue => { tmp.month = newValue; submit() }"
      />
      <div class="col-1"></div>
      <Complete
        class="col"
        :model="tmp.day"
        :options="optionsDay"
        autocomplete="label"
        label="by month"
        :disable="busy"
        @update:model-value="newValue => { tmp.day = newValue; submit() }"
      />
    </div>
    <Complete
      :model="tmp.model"
      :options="values.model"
      label="by model"
      :disable="busy"
      @update:model-value="newValue => { tmp.model = newValue; submit() }"
    />
    <Complete
      :model="tmp.lens"
      :options="values.lens"
      label="by lens"
      :disable="busy"
      @update:model-value="newValue => { tmp.lens = newValue; submit() }"
    />
    <Complete
      :model="tmp.nick"
      :options="nickNames"
      label="by author"
      :disable="busy"
      @update:model-value="newValue => { tmp.nick = newValue; submit() }"
    />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useStore } from "vuex";
import Complete from "./Complete.vue";
import { months } from "../helpers";

const store = useStore();
const route = useRoute();
const router = useRouter();
const busy = computed(() => store.state.app.busy)

const find = computed(() => store.state.app.find)
const tmp = ref({ ...find.value })
const values = computed(() => store.state.app.values)
const nickNames = computed(() => store.getters["app/nickNames"])

// execute typed url
onMounted(() => {
  tmp.value = { ...route.query }
  Object.keys(route.query).forEach((key) => {
    if (route.query[key] == null || route.query[key].length === 0) {
      delete tmp.value[key];
    }
  });
  // adopt to match types
  Object.keys(route.query).forEach((key) => {
    if (["year", "month", "day"].includes(key)) {
      tmp.value[key] = +route.query[key];
    } else if (key === "tags") {
      if (typeof route.query[key] === "string" || route.query[key] instanceof String) {
        tmp.value[key] = [route.query[key]];
      }
    }
  });
  store.commit("app/saveFindForm", tmp.value);
  console.log('Find onMounted');

  if (Object.keys(tmp.value).length) {
    store.commit("app/setBusy", false); // interupt loading
    store.commit("app/resetObjects");
    store.dispatch("app/fetchRecords"); // new filter
    if (route.hash) {
      router.push({ path: "/list", query: tmp.value, hash: route.hash });
    } else {
      router.push({ path: "/list", query: tmp.value });
    }
  }
})

// find field changed
const submit = () => {
  Object.keys(tmp.value).forEach((key) => {
    if (tmp.value[key] == null || tmp.value[key].length === 0) {
      delete tmp.value[key];
    }
  });
  // adopt to match types
  Object.keys(tmp.value).forEach((key) => {
    if (["year", "month", "day"].includes(key)) {
      tmp.value[key] = +tmp.value[key];
    } else if (key === "tags") {
      if (typeof tmp.value[key] === "string" || tmp.value[key] instanceof String) {
        tmp.value[key] = [tmp.value[key]];
      }
    }
  });
  store.commit("app/saveFindForm", tmp.value);
  console.log('Find submit');

  if (Object.keys(tmp.value).length) {
    store.commit("app/setBusy", false); // interupt loading
    store.commit("app/resetObjects");
    store.dispatch("app/fetchRecords"); // new filter
    router.push({ path: "/list", query: tmp.value });
  } else {
    router.replace({ path: "/" }).catch((err) => { });
  }
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
