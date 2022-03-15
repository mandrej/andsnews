<template>
  <q-page class="q-pt-md">
    <q-list separator>
      <q-item>
        <q-item-section>
          <q-item-label>
            <q-input v-model="message" label="Send message to subscribers" />
          </q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-btn :disabled="!fcm_token" color="positive" @click="send" label="Send" />
        </q-item-section>
      </q-item>
    </q-list>
    <q-item-label header>Recount existing field values</q-item-label>
    <q-list separator>
      <q-item v-for="field in Object.keys(values)" :key="field">
        <q-item-section>
          <q-item-label>for {{ field }}</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-btn :disabled="!fcm_token" color="primary" @click="rebuild(field)" label="Rebuild" />
        </q-item-section>
      </q-item>
      <q-item-label header>Fix on {{ formatDatum('2021-12-16', 'DD.MM.YYYY') }}</q-item-label>
      <q-item>
        <q-item-section>
          <q-item-label>Add day field to datastore</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-btn :disabled="!fcm_token" color="primary" @click="fix" label="Fix" />
        </q-item-section>
      </q-item>
      <q-item-label header>Cloud storage related</q-item-label>
      <q-item>
        <q-item-section>
          <q-item-label>Bucket count and size</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-btn :disabled="!fcm_token" color="warning" @click="bucket" label="Recalc" />
        </q-item-section>
      </q-item>
      <q-item>
        <q-item-section>
          <q-item-label>Synchronize datastore records and Cloud bucket</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-btn :disabled="!fcm_token" color="negative" @click="repair" label="Repair" />
        </q-item-section>
      </q-item>
    </q-list>
  </q-page>
</template>

<script setup>
import { computed, ref } from "vue";
import { useStore } from "vuex";
import { api, formatDatum } from "../helpers"

const store = useStore();
const fcm_token = computed(() => store.state.auth.fcm_token)
const message = ref('NEW IMAGES')

const callApi = (url) => {
  api.post(url, { token: fcm_token.value }).then((x) => x.data)
}
const values = computed(() => store.state.app.values)
const rebuild = (name) => {
  callApi('rebuild/' + name)
}
const repair = () => {
  callApi('repair')
}
const fix = () => {
  callApi('fix')
}
const bucket = () => {
  store.dispatch('app/bucketInfo', { verb: 'set' })
}
const send = () => {
  store.dispatch('auth/sendNotifications', message.value)
}
</script>

<style scoped>
.q-btn {
  width: 100px;
}
</style>
