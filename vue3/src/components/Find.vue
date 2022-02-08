<template>
  <div class="q-pa-md q-gutter-md">
    <q-input v-model="tmp.text" :disable="busy" @keyup.enter="submit" label="by text">
      <template v-slot:append>
        <q-icon
          v-if="tmp.text !== ''"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.text = ''; submit()"
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
          v-if="tmp.year !== null"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.year = null; submit()"
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
            v-if="tmp.month !== null"
            class="cursor-pointer"
            name="clear"
            @click.stop="tmp.month = null; submit()"
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
            v-if="tmp.day !== null"
            class="cursor-pointer"
            name="clear"
            @click.stop="tmp.day = null; submit()"
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
          v-if="tmp.model !== null"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.model = null; submit()"
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
          v-if="tmp.lens !== null"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.lens = null; submit()"
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
          v-if="tmp.nick !== null"
          class="cursor-pointer"
          name="clear"
          @click.stop="tmp.nick = null; submit()"
        />
      </template>
    </q-select>
  </div>
</template>

<script>
import { defineComponent, computed, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useStore } from "vuex";

export default defineComponent({
  name: "Find",
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();

    const monthNames = computed(() => {
      const locale = [
        "Jan.",
        "Feb.",
        "Mar.",
        "Apr.",
        "May",
        "Jun.",
        "Jul.",
        "Aug.",
        "Sep.",
        "Oct.",
        "Nov.",
        "Dec.",
      ];
      return locale.map((month, i) => ({ label: month, value: i + 1 }));
    });
    const days = computed(() => {
      const N = 31,
        from = 1,
        step = 1;
      return [...Array(N)].map((_, i) => from + i * step);
    });

    const find = computed(() => store.state.app.find)
    const tmp = ref({ ...find.value });

    function setForm(to) {
      let pid = null;
      if (to.hash) {
        pid = +to.hash.match(/&pid=(.+)/)[1];
      }
      // adopt to match types in store
      if (Object.prototype.hasOwnProperty.call(to.query, "year"))
        to.query.year = +to.query.year;
      if (Object.prototype.hasOwnProperty.call(to.query, "month"))
        to.query.month = +to.query.month;
      if (Object.prototype.hasOwnProperty.call(to.query, "day"))
        to.query.day = +to.query.day;

      store.commit("app/saveFindForm", to.query);
      if (!Object.keys(to.query).length) {
        store.dispatch("app/changeFilter", { reset: false, pid: pid }); // continue
      } else {
        store.dispatch("app/changeFilter", { reset: true, pid: pid }); // new filter
      }
    }

    function submit() {
      // remove undefined and empty list
      Object.keys(tmp.value).forEach((key) => {
        if (tmp.value[key] == null || tmp.value[key].length === 0) {
          delete tmp.value[key];
        }
        // if (Object.prototype.hasOwnProperty.call(tmp.value, "month")) {
        //   tmp.value.month = tmp.value.month.value
        // }
      });
      if (Object.keys(tmp.value).length) {
        router.push({ path: "/list", query: tmp.value });
      } else {
        router.replace({ path: "/" }).catch((err) => { });
      }
    }

    watch(route, (to) => setForm(to));

    return {
      busy: computed(() => store.state.app.busy),
      find,
      values: computed(() => store.state.app.values),
      nickNames: computed(() => store.getters["app/nickNames"]),
      monthNames,
      days,
      tmp,
      submit,
    };
  },
});
</script>
