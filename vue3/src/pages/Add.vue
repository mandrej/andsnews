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
    <div>
      <transition-group
        tag="q-list"
        class="q-mt-md q-list--separator"
        v-if="submitResult.length > 0"
        name="fade"
      >
        <q-item class="bg-grey-2" v-for="rec in submitResult" :key="rec.filename">
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
import { defineAsyncComponent, computed, ref } from 'vue'
import { useStore } from "vuex";
import { CONFIG, api, readExif, notify } from '../helpers'
// import { matCloudUpload } from '@quasar/extras/material-icons'

const Edit = defineAsyncComponent(() =>
  import('../components/Edit.vue')
)

const $q = useQuasar()
const store = useStore();
const user = computed(() => store.state.auth.user)
const files = ref(null);

const percentage = ref(0);
const progress = (evt) => {
  percentage.value = Math.round((evt.loaded * 100) / evt.total)
};
const submitResult = computed(() => store.state.app.uploaded);

const filesChange = (evt) => {
  /**
   * 0: File
      lastModified: 1647531688220
      lastModifiedDate: Thu Mar 17 2022 16:41:28 GMT+0100 (Central European Standard Time) {}
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
      notify("warning", `${file.name} is of unsupported file type`)
    } else if (file.size > CONFIG.fileSize) {
      notify("warning", `${file.name} is too big`)
    } else {
      formData.append(fieldName, file, file.name)
      i++
    }
  })
  if (i > 0) submit(formData);
};

const submit = (formData) => {
  const data = []
  api
    .post('add', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: progress
    })
    .then((x) => x.data) // list
    .then((x) =>
      x.map((item) => {
        if (item.success) {
          data.push(item.rec)
          store.commit('app/addUploaded', item.rec)
        } else {
          notify('negative', `${item.rec.filename} failed to upload`)
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
        notify('negative', 'Timeout error')
      }
    })
};

const showEditForm = (rec) => {
  /**
   * Add headline 'No name', user email and tags: [] to new rec; read exif
   */
  readExif(rec.filename).then(exif => {
    const record = { ...rec, ...{ headline: 'No name', email: user.value.email, tags: [] }, ...exif }
    if (record.flash) {
      record.tags.push('flash')
    }
    window.history.pushState({}, '') // fake history
    $q.dialog({
      component: Edit,
      componentProps: {
        rec: record
      }
    })
  }).catch(err => console.log(err))
}

const removeRecord = (rec) => {
  store.dispatch('app/deleteRecord', rec)
}

// const onRejected = (rejectedEntries) => {
//   // console.log(rejectedEntries);
//   notify('negative', `${rejectedEntries.length} file(s) did not pass validation constraints`)
// }

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
