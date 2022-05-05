<template>
  <Edit v-if="app.showEdit" :rec="current.obj" />

  <q-page class="q-pa-md">
    <div
      class="rounded-borders relative-position bg-grey-2 column justify-center items-center"
      style="height: 150px"
    >
      <div v-if="progressInfos.length > 0">
        Upload in progress. Plase wait ...
      </div>
      <div v-else class="text-body1 text-center" style="width: 70%">
        Drag your images here to upload, or click to browse. Accepts only jpg
        (jpeg) files less then 4 Mb in size.
      </div>
      <input
        type="file"
        multiple
        name="photos"
        @change="filesChange"
        :disabled="inProgress"
      />
      <div class="row absolute-bottom">
        <q-linear-progress
          v-for="(progress, index) in progressInfos"
          :key="index"
          size="10px"
          :value="progress"
          :indeterminate="progress === 1"
          color="warning"
          :style="{ width: 100 / progressInfos.length + '%' }"
        />
      </div>
    </div>

    <div class="q-mt-md">
      <transition-group tag="div" class="row q-col-gutter-md" name="fade">
        <div
          v-for="rec in uploaded"
          :key="rec.filename"
          class="col-xs-6 col-sm-4 col-md-4 col-lg-3 col-xl-2"
        >
          <q-card class="bg-grey-2" flat>
            <q-img :src="fullsized + rec.filename" :ratio="3 / 2">
              <template #error>
                <img src="/broken.svg" />
              </template>
              <q-badge floating class="text-black" color="warning">
                {{ formatBytes(rec.size) }}
              </q-badge>
            </q-img>
            <q-card-actions class="q-py-sm justify-between">
              <q-btn
                flat
                round
                color="grey"
                icon="delete"
                @click="removeRecord(rec)"
              />
              <q-btn
                flat
                round
                color="grey"
                icon="publish"
                @click="edit(rec)"
              />
            </q-card-actions>
          </q-card>
        </div>
      </transition-group>
    </div>
  </q-page>
</template>

<script setup>
import { defineAsyncComponent, computed, reactive, ref } from "vue";
import { useAppStore } from "../stores/app";
import { useAuthStore } from "../stores/auth";
import {
  CONFIG,
  api,
  fullsized,
  readExif,
  formatBytes,
  notify,
} from "../helpers";

const Edit = defineAsyncComponent(() => import("../components/Edit.vue"));

const app = useAppStore();
const auth = useAuthStore();
const user = computed(() => auth.user);
// const fcm_token = computed(() => auth.fcm_token);
let files = reactive([]);
let progressInfos = reactive([]);
const inProgress = ref(false);

const uploaded = computed(() => app.uploaded);
const current = reactive({ obj: null });

const filesChange = (evt) => {
  /**
   * 0: File
      name: "DSC_8082-22-03-14-819.jpg"
      size: 1858651
      type: "image/jpeg"
   */
  let fileList = evt.target.files;
  let fieldName = evt.target.name; // photos
  if (!fileList.length) return;

  inProgress.value = true;
  Array.from(fileList).map((file) => {
    if (file.type !== CONFIG.fileType) {
      notify({
        type: "warning",
        message: `${file.name} is of unsupported file type`,
      });
    } else if (file.size > CONFIG.fileSize) {
      notify({ type: "warning", message: `${file.name} is too big` });
    } else {
      files.push(file);
    }
  });

  for (let i = 0; i < files.length; i++) {
    upload(i, fieldName, files[i]);
  }

  // setTimeout(() => {
  //   files = [];
  //   progressInfos = [];
  //   inProgress.value = false;
  // }, 60000);
};

const upload = async (idx, name, file) => {
  const formData = new FormData();
  formData.append(name, file);
  // formData.append("token", fcm_token.value);
  progressInfos[idx] = 0;

  api
    .post("add", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (evt) => {
        progressInfos[idx] = evt.loaded / evt.total;
      },
    })
    .then((res) => {
      // progressInfos[idx] = 0;
      if (res.data.success) {
        app.uploaded.push(res.data.rec);
      } else {
        notify({
          type: "negative",
          message: `${res.data.rec.filename} failed to upload`,
        });
      }
      progressInfos.splice(idx, 1);
      files.splice(idx, 1);
    })
    .catch((err) => {
      progressInfos.splice(idx, 1);
      files.splice(idx, 1);
      notify({ type: "negative", message: err.message });
    })
    .finally(() => {});
};

const edit = async (rec) => {
  /**
   * Add user email and tags: [] to new rec; read exif
   */
  const exif = await readExif(rec.filename);
  const record = Object.assign(
    { email: user.value.email, tags: [] },
    rec,
    exif
  );
  if (record.flash) {
    record.tags.push("flash");
  }
  current.obj = ref(record);
  window.history.pushState(history.state, ""); // fake history
  app.showEdit = true;
};

const removeRecord = (rec) => {
  app.deleteRecord(rec);
};
</script>

<style scoped>
input {
  opacity: 0;
  width: 100%;
  height: inherit;
  position: absolute;
  cursor: pointer;
}
.disabled,
[disabled] {
  opacity: 0 !important;
}
</style>
