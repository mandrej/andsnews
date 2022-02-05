<template>
  <div class="q-pa-md">
    <div class="column justify-center items-center position-relative" style="height: 150px;">
      <div class="text-body1">
        Drag your images here to upload, or click to browse.
        <br />Accepts only jpg (jpeg) files less then 4 Mb in size.
      </div>
      <input
        type="file"
        multiple
        name="photos"
        @change="filesChange($event.target.name, $event.target.files)"
        accept=".jpg, .jpeg, image/jpeg"
        class="input-file"
      />
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
      <q-list v-if="submitResult.length > 0" separator>
        <q-item v-for="rec in submitResult" :key="rec.filename">
          <q-item-section>
            <q-item-label>{{ rec.filename }}</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-btn label="Remove" type="button" color="negative" @click="removeRecord(rec)" />
          </q-item-section>
          <q-item-section side>
            <q-btn label="Publish" type="button" color="primary" @click="showEditForm(rec)" />
          </q-item-section>
        </q-item>
      </q-list>
    </div>
  </div>
</template>

<script>
import { useQuasar } from 'quasar'
import { defineComponent, computed, ref } from 'vue'
import { useStore } from "vuex";
import Edit from "../components/Edit.vue"
import { CONFIG, api, notify } from '../helpers'

export default defineComponent({
  setup() {
    const $q = useQuasar()
    const store = useStore();
    const user = computed(() => store.state.auth.user)
    const files = ref(null);
    const percentage = ref(0);
    const progress = (evt) => {
      percentage.value = Math.round((evt.loaded * 100) / evt.total)
    };
    const submitResult = computed(() => store.state.app.uploaded);

    const filesChange = (fieldName, fileList) => {
      const formData = new FormData()
      if (!fileList.length) return
      Array.from(Array(fileList.length).keys()).map((x) => {
        if (fileList[x].type !== CONFIG.fileType) {
          notify("warning", `${fileList[x].name} is of unsupported file type`)
        } else if (fileList[x].size > CONFIG.fileSize) {
          notify("warning", `${fileList[x].name} is too big`)
        } else {
          formData.append(fieldName, fileList[x], fileList[x].name)
        }
      })
      let i = 0
      for (let pair of formData.entries()) {
        i++
      }
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
       * Add headline 'No name' and user email to new rec
       */
      $q.dialog({
        component: Edit,
        componentProps: {
          rec: { ...rec, ...{ headline: 'No name', email: user.value.email } }
        }
      })
    }

    return {
      api,
      files,
      user,
      percentage,
      progress,
      CONFIG,

      submit,
      filesChange,
      submitResult,
      showEditForm,

      removeRecord(rec) {
        store.dispatch('app/deleteRecord', rec)
      },

      onRejected(rejectedEntries) {
        // console.log(rejectedEntries);
        notify('negative', `${rejectedEntries.length} file(s) did not pass validation constraints`)
      }
    }
  }
})
</script>

<style>
.input-file {
  opacity: 0;
  width: 100%;
  height: inherit;
  position: absolute;
  cursor: pointer;
}
</style>
