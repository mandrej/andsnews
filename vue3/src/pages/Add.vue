<template>
  <div class="q-pa-md">
    <div
      class="bg-grey-2 column justify-center items-center"
      style="position: relative; height: 150px;"
    >
      <div class="text-body1 text-center" style="width: 70%">
        Drag your images here to upload, or click to browse.
        <br />Accepts only jpg (jpeg) files less then 4 Mb in size.
      </div>
      <input type="file" multiple name="photos" @change="filesChange" />
    </div>
    <div>
      <q-linear-progress
        size="10px"
        :value="percentage"
        :indeterminate="percentage === 100"
        color="warning"
      />
    </div>
    <div v-if="uploaded.length > 0">
      <transition-group tag="q-list" class="q-mt-md q-list--separator" name="fade">
        <q-item v-for="rec in uploaded" :key="rec.filename" class="bg-grey-2">
          <q-item-section>
            <q-item-label>{{ rec.filename }}</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-btn
              :label="$q.screen.gt.xs ? 'Remove' : null"
              type="button"
              color="negative"
              icon="delete"
              @click="removeRecord(rec)"
            />
          </q-item-section>
          <q-item-section side>
            <q-btn
              :label="$q.screen.gt.xs ? 'Publish' : null"
              type="button"
              color="primary"
              icon="publish"
              @click="showEditForm(rec)"
            />
          </q-item-section>
        </q-item>
      </transition-group>
    </div>
  </div>
</template>

<script setup>
import { useQuasar } from 'quasar'
import { computed, ref } from 'vue'
import { useAppStore } from "../store/app";
import { useAuthStore } from "../store/auth";
import Edit from "../components/Edit.vue"
import { CONFIG, api, readExif, notify } from '../helpers'

const $q = useQuasar()
const app = useAppStore();
const auth = useAuthStore();
const user = computed(() => auth.user)
const files = ref(null);

const percentage = ref(0);
const progress = (evt) => {
  percentage.value = Math.round((evt.loaded * 100) / evt.total)
};
const uploaded = computed(() => app.uploaded);

const filesChange = (evt) => {
  /**
   * 0: File
      name: "DSC_8082-22-03-14-819.jpg"
      size: 1858651
      type: "image/jpeg"
   */
  const fileList = evt.target.files
  const fieldName = evt.target.name
  if (!fileList.length) return
  const formData = new FormData()
  let i = 0
  Array.from(fileList).map(file => {
    if (file.type !== CONFIG.fileType) {
      notify({ type: "warning", message: `${file.name} is of unsupported file type` })
    } else if (file.size > CONFIG.fileSize) {
      notify({ type: "warning", message: `${file.name} is too big` })
    } else {
      formData.append(fieldName, file, file.name)
      i++
    }
  })
  if (i > 0) submit(formData);
};

const submit = (formData) => {
  api
    .post('add', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: progress
    })
    .then((x) => x.data) // list
    .then((x) =>
      x.map((item) => {
        if (item.success) {
          app.uploaded.push(item.rec)
        } else {
          notify({ type: 'negative', message: `${item.rec.filename} failed to upload` })
        }
      })
    )
    .then(() => {
      files.value = null
      percentage.value = 0
    })
    .catch(err => {
      if (err.code === 'ECONNABORTED') {
        files.value = null
        percentage.value = 0
        notify({ type: 'negative', message: 'Timeout error' })
      }
    })
};

const showEditForm = async (rec) => {
  /**
   * Add headline 'No name', user email and tags: [] to new rec; read exif
   */
  const exif = await readExif(rec.filename);
  const record = Object.assign({ headline: 'No name', email: user.value.email, tags: [] }, rec, exif)
  if (record.flash) {
    record.tags.push('flash')
  }
  app.current = ref(record)
  window.history.pushState({}, '') // fake history
  $q.dialog({
    component: Edit,
  })
}

const removeRecord = (rec) => {
  app.deleteRecord(rec)
}
</script>

<style>
input {
  opacity: 0;
  width: 100%;
  height: inherit;
  position: absolute;
  cursor: pointer;
}
</style>
