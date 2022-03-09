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
import { onMounted, computed, reactive, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useStore } from "vuex";
import Complete from "./Complete.vue";
import { months } from "../helpers";

const store = useStore();
const route = useRoute();
const router = useRouter();
const busy = computed(() => store.state.app.busy)

const find = computed(() => store.state.app.find)
let tmp = reactive({ ...find.value })
const values = computed(() => store.state.app.values)
const nickNames = computed(() => store.getters["app/nickNames"])

watch(find, (query) => dispatch(query), { deep: true });
const dispatch = (query) => {
  if (Object.keys(query).length) {
    store.commit("app/setBusy", false); // interupt loading
    store.commit("app/resetObjects");
    store.dispatch("app/fetchRecords"); // new filter
    if (route.hash) {
      router.push({ path: "/list", query: query, hash: route.hash });
    } else {
      router.push({ path: "/list", query: query });
    }
  } else {
    router.push({ path: "/" }).catch((err) => { });
  }
}

// execute typed url
onMounted(() => {
  tmp = route.query
  Object.keys(route.query).forEach((key) => {
    if (route.query[key] == null || route.query[key].length === 0) {
      delete tmp[key];
    }
  });
  // adopt to match types
  Object.keys(route.query).forEach((key) => {
    if (["year", "month", "day"].includes(key)) {
      tmp[key] = +route.query[key];
    } else if (key === "tags") {
      if (typeof route.query[key] === "string" || route.query[key] instanceof String) {
        tmp[key] = [route.query[key]];
      }
    }
  });
  store.commit("app/saveFindForm", { ...tmp });
})



// find field changed
const submit = () => {
  Object.keys(tmp).forEach((key) => {
    if (tmp[key] == null) {
      delete tmp[key];
    }
  });
  // adopt to match types
  Object.keys(tmp).forEach((key) => {
    if (["year", "month", "day"].includes(key)) {
      tmp[key] = +tmp[key];
    } else if (key === "tags") {
      if (typeof tmp[key] === "string" || tmp[key] instanceof String) {
        tmp[key] = [tmp[key]];
      }
    }
  });
  store.commit("app/saveFindForm", { ...tmp });
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
