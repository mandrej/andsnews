<template>
  <q-page>
    <div class="q-pa-md" v-for="(list, datum) in objectsByDate" :key="datum">
      <q-scroll-observer @scroll="scrollHandler" />
      <div class="text-h6">{{ datum }}</div>
      <div v-viewer="options" class="row q-col-gutter-md">
        <div
          class="col-xs-12 col-sm-6 col-md-4 col-lg-3 col-xl-2"
          v-for="item in list"
          :key="item.id"
        >
          <q-card>
            <img
              class="thumbnail"
              :src="smallsized + item.filename"
              :data-source="fullsized + item.filename"
              :alt="item.headline"
            />
            <q-card-section class="q-pb-none">
              <div class="text-subtitle1 ellipsis">{{ item.headline }}</div>
            </q-card-section>
            <q-card-section class="row justify-between q-py-none">
              <div style="line-height: 42px;">{{ item.nick }}, {{ item.date }}</div>
              <q-btn v-if="item.loc" flat round color="grey" icon="map" />
            </q-card-section>
            <q-card-actions class="justify-between q-pt-none">
              <q-btn flat round color="grey" icon="delete" @click="showConfirm(item)" />
              <q-btn flat round color="grey" icon="edit" @click="showEditForm(item)" />
              <!-- <q-btn flat round color="grey" icon="share" /> -->
              <q-btn
                flat
                round
                color="grey"
                icon="download"
                @click.stop="download"
                :href="`/api/download/${item.filename}`"
                :download="item.filename"
              />
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
import { useQuasar } from 'quasar'
import { defineComponent, computed, ref } from "vue";
import { useStore } from "vuex";
import { smallsized, fullsized } from "../helpers";
import Edit from "../components/Edit.vue"
import VueViewer, { Viewer, directive } from "v-viewer"

export default defineComponent({
  name: "List",
  directives: {
    viewer: directive({
      debug: true,
    }),
  },
  setup() {
    const $q = useQuasar()
    const store = useStore();
    const next = computed(() => store.state.app.next);
    const error = computed(() => store.state.app.error);

    const scrollHandler = (obj) => {
      const scrollHeight = document.documentElement.scrollHeight;
      if (
        scrollHeight - obj.position.top < 3000 &&
        obj.direction === "down" &&
        next
      ) {
        store.dispatch("app/fetchRecords");
      }
    }

    // const format = (dateStr, from, to) => {
    //   const dt = date.extractDate(item.date, from)
    //   return date.formatDate(dt, to)
    // }

    const showEditForm = (rec) => {
      $q.dialog({
        component: Edit,
        componentProps: {
          rec: rec
        }
      }).onOk(() => {
        console.log('OK')
      }).onCancel(() => {
        console.log('Cancel')
      })
    }
    const showConfirm = (rec) => {
      $q.dialog({
        title: 'Confirm Delete',
        message: `Would you like to delete ${rec.headline}?`,
        cancel: true,
        persistent: true
      }).onOk(() => {
        store.dispatch('app/deleteRecord', rec)
      })
    }

    return {
      error,
      smallsized,
      fullsized,
      objectsByDate: computed(() => store.getters["app/objectsByDate"]),
      scrollHandler,
      showEditForm,
      showConfirm,
      download: () => {
        return null
        // this.$emit('register-download', {
        //   headline: this.item.headline,
        //   email: this.user.email
        // })
      },
      options: {
        toolbar: false,
        url: 'data-source',
      }
    };
  },
});
</script>

<style lang="scss" scoped>
.thumbnail {
  display: block;
  width: 100%;
  height: 200px;
  object-fit: cover;
}
</style>
