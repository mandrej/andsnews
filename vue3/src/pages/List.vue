<template>
  <q-page>
    <q-banner v-if="error === 0" class="bg-warning q-ma-md q-pa-md" rounded>
      <template v-slot:avatar>
        <q-icon name="warning" color="primary" />
      </template>
      No data found for current filter/ search
    </q-banner>

    <div class="q-pa-md" v-for="(list, datum) in objectsByDate" :key="datum">
      <q-scroll-observer @scroll="scrollHandler" />
      <div class="text-h6 text-weight-light">{{ formatDatum(datum, 'dddd DD.MM.YYYY') }}</div>
      <div class="row q-col-gutter-md">
        <div
          class="col-xs-12 col-sm-6 col-md-4 col-lg-3 col-xl-2"
          v-for="item in list"
          :key="item.id"
        >
          <q-card flat bordered>
            <q-img
              class="thumbnail cursor-pointer"
              :src="smallsized + item.filename"
              @click="showCarousel(item.id)"
            >
              <div class="absolute-bottom text-subtitle2">{{ item.headline }}</div>
            </q-img>
            <q-card-section class="row justify-between q-py-none">
              <div style="line-height: 42px;">
                {{ item.nick }},
                <router-link
                  :to="{ path: '/list', query: { year: item.year, month: item.month, day: item.day } }"
                  class="text-secondary"
                  style="text-decoration: none;"
                >{{ formatDatum(item.date, 'DD.MM.YYYY') }}</router-link>
                {{ item.date.substring(11) }}
              </div>
              <q-btn
                v-if="item.loc"
                flat
                round
                color="grey"
                icon="my_location"
                target="blank"
                :href="
                  'https://www.google.com/maps/search/?api=1&query=' + [...item.loc]
                "
              />
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

    <q-page-scroller position="bottom-right" :scroll-offset="150" :offset="[18, 18]">
      <q-btn fab icon="arrow_upward" color="secondary" />
    </q-page-scroller>
  </q-page>
</template>

<script>
import { useQuasar } from 'quasar'
import { defineComponent, defineAsyncComponent, computed } from "vue";
import { useStore } from "vuex";
import { smallsized, formatDatum } from "../helpers";
import Carousel from "../components/Carousel.vue"

const Edit = defineAsyncComponent(() =>
  import('../components/Edit.vue')
)

export default defineComponent({
  name: "List",
  setup() {
    const $q = useQuasar()
    const store = useStore();
    const next = computed(() => store.state.app.next);
    const error = computed(() => store.state.app.error);
    const objectsByDate = computed(() => store.getters["app/objectsByDate"]);

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

    const showEditForm = (rec) => {
      $q.dialog({
        component: Edit,
        componentProps: {
          rec: rec
        }
      }).onOk(() => {
        // console.log('OK')
      }).onCancel(() => {
        // console.log('Cancel')
      })
    }
    const showConfirm = (rec) => {
      $q.dialog({
        title: 'Confirm Delete',
        message: `Would you like to delete ${rec.headline}?`,
        ok: {
          color: 'negative',
          flat: true
        },
        cancel: {
          color: 'positive',
          flat: true
        },
        persistent: true
      }).onOk(() => {
        store.dispatch('app/deleteRecord', rec)
      })
    }

    return {
      error,
      smallsized,
      formatDatum,
      objectsByDate,
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
      showCarousel: (id) => {
        $q.dialog({
          component: Carousel,
          componentProps: {
            pid: id
          }
        }).onOk(() => {
          // console.log('OK')
        }).onCancel(() => {
          // console.log('Cancel')
        })
      },
    };
  },
});
</script>

<style scoped>
.thumbnail {
  height: 250px;
}
.vel-modal {
  background: rgba(0, 0, 0, 1);
}
</style>
