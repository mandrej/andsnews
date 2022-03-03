<template>
  <div class="q-pa-md q-gutter-md">
    <q-input v-model="tmp.text" :disable="busy" @keyup.enter="submit" label="by text" clearable />
    <q-select
      :disable="busy"
      v-model="tmp.tags"
      :options="optionsTagsRef"
      use-input
      clearable
      fill-input
      hide-selected
      input-debounce="0"
      @filter="filterTags"
      @update:model-value="submit"
      label="by tag"
    >
      <!-- <template v-slot:append>
        <q-icon
          v-if="tmp.tags && tmp.tags.length !== 0"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.tags = []; submit()"
        />
      </template>-->
    </q-select>
    <q-select
      :disable="busy"
      v-model="tmp.year"
      :options="values.year"
      @update:model-value="submit"
      label="by year"
      clearable
    />
    <div class="row">
      <q-select
        class="col"
        :disable="busy"
        v-model="tmp.month"
        :options="monthNames"
        @update:model-value="submit"
        clearable
        emit-value
        map-options
        label="by month"
      />
      <div class="col-1"></div>
      <q-select
        class="col"
        :disable="busy"
        v-model="tmp.day"
        :options="days"
        @update:model-value="submit"
        label="by day"
        clearable
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

const store = useStore();
const route = useRoute();
const router = useRouter();
const busy = computed(() => store.state.app.busy)

const find = computed(() => store.state.app.find)
const tmp = ref({ ...find.value })
const values = computed(() => store.state.app.values)
const nickNames = computed(() => store.getters["app/nickNames"])

// execute stored values
onMounted(() => {
  // remove undefined and empty list
  Object.keys(route.query).forEach((key) => {
    if (route.query[key] == undefined || route.query[key].length === 0) {
      delete route.query[key];
    }
  });
  // adopt to match types in store
  Object.keys(route.query).forEach((key) => {
    if (['year', 'month', 'day'].includes(key)) {
      route.query[key] = +route.query[key]
    }
  });
  store.commit("app/saveFindForm", route.query);

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

// field changed
const submit = () => {
  // remove undefined and empty list
  Object.keys(tmp.value).forEach((key) => {
    if (tmp.value[key] == null || tmp.value[key].length === 0) {
      delete tmp.value[key];
    }
  });
  // adopt to match types in store
  Object.keys(tmp.value).forEach((key) => {
    if (['year', 'month', 'day'].includes(key)) {
      tmp.value[key] = +tmp.value[key]
    }
  });
  store.commit("app/saveFindForm", tmp.value);

  if (Object.keys(tmp.value).length) {
    store.commit("app/setBusy", false); // interupt loading
    store.commit("app/resetObjects");
    store.dispatch("app/fetchRecords"); // new filter
    router.push({ path: "/list", query: tmp.value });
  } else {
    router.replace({ path: "/" }).catch((err) => { });
  }
}

const monthNames = computed(() => {
  const locale = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];
  return locale.map((month, i) => ({ label: month, value: i + 1 }));
})
const days = computed(() => {
  const N = 31,
    from = 1,
    step = 1;
  return [...Array(N)].map((_, i) => from + i * step);
})

// autocmplete
const optionsTags = [...values.value.tags]
const optionsTagsRef = ref(optionsTags)
function filterTags(val, update) {
  if (val === '') {
    update(() => {
      optionsTagsRef.value = optionsTags
    })
    return
  }
  update(() => {
    const needle = val.toLowerCase()
    optionsTagsRef.value = optionsTags.filter(v => v.toLowerCase().indexOf(needle) > -1)
  })
}
// function setTags(val) {
//   // @update:model-value="submit"
//   console.log(val);
//   console.log(tmp.tags);
//   tmp.tags.value = val
//   submit()
// }
</script>
