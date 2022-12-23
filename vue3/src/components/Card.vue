<template>
  <q-card v-bind="cardAttributes(rec.filename)" flat>
    <q-img
      class="cursor-pointer"
      :ratio="5 / 4"
      :src="rec.id ? smallsized + rec.filename : fullsized + rec.filename"
      no-spinner
      @click="
        emit('carouselShow', rec.filename);
        analytics('popular-picture');
      "
    >
      <template #error>
        <img src="/broken.svg" />
      </template>
      <div v-if="rec.id" class="absolute-bottom text-subtitle2">
        {{ rec.headline }}
      </div>
      <q-badge v-else floating class="text-black" color="warning">
        {{ formatBytes(rec.size) }}
      </q-badge>
    </q-img>
    <q-card-section v-if="rec.id" class="row justify-between q-py-none">
      <div style="line-height: 42px">
        {{ rec.nick }},
        <router-link
          :to="{
            path: '/list',
            query: {
              year: rec.year,
              month: rec.month,
              day: rec.day,
            },
          }"
          class="text-secondary"
          style="text-decoration: none"
          >{{ formatDatum(rec.date, "DD.MM.YYYY") }}</router-link
        >
        {{ rec.date.substring(11) }}
      </div>
      <q-btn
        v-if="rec.loc"
        flat
        round
        color="grey"
        icon="my_location"
        target="blank"
        :href="
          'https://www.google.com/maps/search/?api=1&query=' + [...rec.loc]
        "
      />
    </q-card-section>
    <q-card-actions
      v-if="isAuthorOrAdmin"
      class="justify-between"
      :class="{ 'q-pt-none': Boolean(rec.id) }"
    >
      <q-btn
        flat
        round
        color="grey"
        icon="delete"
        @click="rec.id ? emit('confirmDelete', rec) : emit('deleteRecord', rec)"
      />
      <q-btn
        flat
        round
        color="grey"
        :icon="rec.id ? 'edit' : 'publish'"
        @click="emit('editRecord', rec)"
      />
      <q-btn
        v-if="rec.id"
        flat
        round
        color="grey"
        icon="share"
        @click="onShare"
      />
      <q-btn
        v-if="rec.id"
        flat
        round
        color="grey"
        icon="download"
        :href="`/api/download/${props.rec.filename}`"
        :download="rec.filename"
        @click.stop="analytics('download-picture')"
      />
    </q-card-actions>
  </q-card>
</template>

<script setup>
import { copyToClipboard } from "quasar";
import { computed } from "vue";
import { useAuthStore } from "../stores/auth";
import {
  smallsized,
  fullsized,
  formatDatum,
  formatBytes,
  cardAttributes,
  notify,
  U,
} from "../helpers";

const emit = defineEmits([
  "carouselShow",
  "confirmDelete",
  "editRecord",
  "deleteRecord",
]);
const props = defineProps({
  rec: Object,
});

const auth = useAuthStore();
const user = computed(() => auth.user);

const isAuthorOrAdmin = () => {
  return user.value.isAdmin || user.value.email === props.rec.email;
};

const onShare = () => {
  const url = window.location.href + "#" + U + props.rec.filename;
  copyToClipboard(url)
    .then(() => {
      notify({ type: "info", message: "URL copied to clipboard" });
    })
    .catch(() => {
      notify({ type: "warning", message: "Unable to copy URL to clipboard" });
    });
};
const analytics = (event_name) => {
  /**
   * popular-picture
   * download-picture
   *
   */
  gtag("event", event_name, {
    filename: props.rec.filename,
    user: user.value && user.value.email ? user.value.email : "anonymous",
    count: 1,
  });
};
</script>
