<template>
  <div class="q-pa-md q-gutter-md">
    <q-input v-model="tmp.text" :disable="busy" @keyup.enter="submit" label="by text">
      <template v-slot:append>
        <q-icon
          v-if="tmp.text !== undefined"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.text = undefined; submit()"
        />
      </template>
    </q-input>
    <q-select
      v-model="tmp.tags"
      :options="values.tags"
      :disable="busy"
      @update:model-value="submit"
      multiple
      label="by tag"
    >
      <template v-slot:append>
        <q-icon
          v-if="tmp.tags && tmp.tags.length !== 0"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.tags = []; submit()"
        />
      </template>
    </q-select>
    <q-select
      v-model="tmp.year"
      :options="values.year"
      :disable="busy"
      @update:model-value="submit"
      label="by year"
    >
      <template v-slot:append>
        <q-icon
          v-if="tmp.year !== undefined"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.year = undefined; submit()"
        />
      </template>
    </q-select>
    <div class="row">
      <q-select
        class="col"
        v-model="tmp.month"
        :options="monthNames"
        :disable="busy"
        @update:model-value="submit"
        emit-value
        map-options
        label="by month"
      >
        <template v-slot:append>
          <q-icon
            v-if="tmp.month !== undefined"
            class="cursor-pointer"
            name="clear"
            @click.stop="tmp.month = undefined; submit()"
          />
        </template>
      </q-select>
      <div class="col-1"></div>
      <q-select
        class="col"
        v-model="tmp.day"
        :options="days"
        :disable="busy"
        @update:model-value="submit"
        label="by day"
      >
        <template v-slot:append>
          <q-icon
            v-if="tmp.day !== undefined"
            class="cursor-pointer"
            name="clear"
            @click.stop="tmp.day = undefined; submit()"
          />
        </template>
      </q-select>
    </div>
    <q-select
      v-model="tmp.model"
      :options="values.model"
      :disable="busy"
      @update:model-value="submit"
      label="by model"
    >
      <template v-slot:append>
        <q-icon
          v-if="tmp.model !== undefined"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.model = undefined; submit()"
        />
      </template>
    </q-select>
    <q-select
      v-model="tmp.lens"
      :options="values.lens"
      :disable="busy"
      @update:model-value="submit"
      label="by lens"
    >
      <template v-slot:append>
        <q-icon
          v-if="tmp.lens !== undefined"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.lens = undefined; submit()"
        />
      </template>
    </q-select>
    <q-select
      v-model="tmp.nick"
      :options="nickNames"
      :disable="busy"
      @update:model-value="submit"
      label="by author"
    >
      <template v-slot:append>
        <q-icon
          v-if="tmp.nick !== undefined"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.nick = undefined; submit()"
        />
      </template>
    </q-select>
  </div>
</template>

<script>
import { defineComponent, computed, onMounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useStore } from "vuex";

export default defineComponent({
  name: "Find",
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();

    const find = computed(() => store.state.app.find)
    const tmp = computed(() => {
      return { ...find.value }
    })

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
        router.push({ path: "/list", query: tmp.value, hash: route.hash });
      }
    })

    // click on router-link
    watch(route, (to, old) => setForm(to, old));

    const setForm = (to, old) => {
      if (JSON.stringify(to.query) === JSON.stringify(old.query)) return
      // remove undefined and empty list
      Object.keys(to.query).forEach((key) => {
        if (to.query[key] == null || to.query[key].length === 0) {
          delete to.query[key];
        }
      });
      // adopt to match types in store
      Object.keys(to.query).forEach((key) => {
        if (['year', 'month', 'day'].includes(key)) {
          to.query[key] = +to.query[key]
        }
      });
      store.commit("app/saveFindForm", to.query);

      if (Object.keys(to.query).length) {
        store.commit("app/setBusy", false); // interupt loading
        store.commit("app/resetObjects");
        store.dispatch("app/fetchRecords"); // new filter
        router.push({ path: "/list", query: tmp.value, hash: to.hash });
      }
    }

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
        router.push({ path: "/list", query: tmp.value });
      } else {
        router.replace({ path: "/" }).catch((err) => { });
      }
    }

    return {
      tmp,
      busy: computed(() => store.state.app.busy),
      values: computed(() => store.state.app.values),
      nickNames: computed(() => store.getters["app/nickNames"]),
      monthNames: computed(() => {
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
      }),
      days: computed(() => {
        const N = 31,
          from = 1,
          step = 1;
        return [...Array(N)].map((_, i) => from + i * step);
      }),
      submit,
    };
  },
});
</script>
