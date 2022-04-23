<template>
  <Edit v-if="app.showEdit" :rec="current.obj" />

  <q-page class="q-pa-md">
    <div
      class="rounded-borders relative-position bg-grey-2 column justify-center items-center"
      style="height: 150px"
    >
      <div
        v-if="percentage === 0"
        class="text-body1 text-center"
        style="width: 70%"
      >
        Drag your images here to upload, or click to browse. Accepts only jpg
        (jpeg) files less then 4 Mb in size.
      </div>
      <div v-else-if="percentage < 1">Plase wait ...</div>
      <div v-else-if="percentage === 1">Processing images ...</div>
      <input type="file" multiple name="photos" @change="filesChange" />
      <q-linear-progress
        class="absolute-bottom"
        size="10px"
        :value="percentage"
        :indeterminate="percentage === 1"
        color="warning"
      />
    </div>

    <div class="q-mt-md">
      <transition-group tag="div" class="row q-col-gutter-md" name="fade">
        <div
          v-for="rec in uploaded"
          :key="rec.filename"
          class="col-xs-6 col-sm-4 col-md-4 col-lg-3 col-xl-2"
        >
          <q-card class="bg-grey-2" flat>
            <q-card-section class="justify-between" horizontal>
              <q-avatar rounded size="72px">
                <q-img :src="fullsized + rec.filename">
                  <template #error>
                    <img src="/broken.svg" />
                  </template>
                </q-img>
                <q-badge floating color="primary">{{
                  formatBytes(rec.size)
                }}</q-badge>
              </q-avatar>
              <q-card-actions>
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
            </q-card-section>
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
const files = ref(null);
const current = reactive({ obj: null });

const uploaded = computed(() => app.uploaded);
const percentage = computed({
  get() {
    return app.percentage;
  },
  set(newValue) {
    app.percentage = newValue;
  },
});
const progress = (evt) => {
  percentage.value = evt.loaded / evt.total;
};

const filesChange = (evt) => {
  /**
   * 0: File
      name: "DSC_8082-22-03-14-819.jpg"
      size: 1858651
      type: "image/jpeg"
   */
  const fileList = evt.target.files;
  const fieldName = evt.target.name;
  if (!fileList.length) return;
  const formData = new FormData();
  let i = 0;
  Array.from(fileList).map((file) => {
    if (file.type !== CONFIG.fileType) {
      notify({
        type: "warning",
        message: `${file.name} is of unsupported file type`,
      });
    } else if (file.size > CONFIG.fileSize) {
      notify({ type: "warning", message: `${file.name} is too big` });
    } else {
      formData.append(fieldName, file, file.name);
      i++;
    }
  });
  if (i > 0) submit(formData);
};

const submit = (formData) => {
  api
    .post("add", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: progress,
    })
    .then((x) => x.data) // list
    .then((x) =>
      x.map((item) => {
        if (item.success) {
          app.uploaded.push(item.rec);
        } else {
          notify({
            type: "negative",
            message: `${item.rec.filename} failed to upload`,
          });
        }
      })
    )
    .then(() => {
      files.value = null;
      percentage.value = 0;
    })
    .catch((err) => {
      files.value = null;
      percentage.value = 0;
      if (err.code === "ECONNABORTED") {
        notify({ type: "negative", message: "Timeout error" });
      }
    });
};

const edit = async (rec) => {
  /**
   * Add headline 'No name', user email and tags: [] to new rec; read exif
   */
  const exif = await readExif(rec.filename);
  const record = Object.assign(
    { headline: "No name", email: user.value.email, tags: [] },
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
</style>
