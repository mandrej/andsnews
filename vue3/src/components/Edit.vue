<template>
  <q-dialog
    v-model="app.showEdit"
    :maximized="$q.screen.lt.md"
    transition-show="slide-up"
    transition-hide="slide-down"
    persistent
  >
    <q-card class="q-dialog-plugin full-width" style="max-width: 800px">
      <q-toolbar class="bg-grey-2 text-black row justify-between" bordered>
        <div>
          <q-btn
            color="primary"
            type="submit"
            label="Submit"
            @click="onSubmit"
          />
          <q-btn
            v-if="user.isAdmin"
            class="q-ml-sm gt-sm"
            flat
            label="Read Exif"
            @click="getExif"
          />
        </div>
        <div>{{ formatBytes(tmp.size) }}</div>
        <div>
          <q-btn flat round dense icon="close" @click="onCancel" />
        </div>
      </q-toolbar>
      <q-card-section>
        <q-form
          autofocus
          autocorrect="off"
          autocapitalize="off"
          autocomplete="off"
          spellcheck="false"
          @submit="onSubmit"
        >
          <div class="row q-col-gutter-md">
            <div class="col-xs-12 col-sm-4 gt-xs">
              <q-img :ratio="1" :src="smallsized + tmp.filename">
                <template #error>
                  <img src="/broken.svg" />
                </template>
              </q-img>
            </div>
            <div class="col-xs-12 col-sm-8 col-8">
              <q-input
                v-model="tmp.headline"
                label="Headline"
                :placeholder="CONFIG.noTitle"
                :hint="`Image without name is called '${CONFIG.noTitle}'. Required`"
                @blur="
                  tmp.headline === undefined || tmp.headline === ''
                    ? (tmp.headline = CONFIG.noTitle)
                    : tmp.headline
                "
                autofocus
              />
              <q-input v-model="tmp.filename" label="Filename" readonly />
              <q-select
                v-model="tmp.email"
                :options="values.email"
                label="Author"
              />
              <q-input v-model="tmp.date" label="Date taken">
                <template #prepend>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy
                      cover
                      transition-show="scale"
                      transition-hide="scale"
                    >
                      <q-date v-model="tmp.date" mask="YYYY-MM-DD HH:mm">
                        <div class="row items-center justify-end">
                          <q-btn
                            v-close-popup
                            label="Close"
                            color="primary"
                            flat
                          />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>
                <template #append>
                  <q-icon name="access_time" class="cursor-pointer">
                    <q-popup-proxy
                      cover
                      transition-show="scale"
                      transition-hide="scale"
                    >
                      <q-time
                        v-model="tmp.date"
                        mask="YYYY-MM-DD HH:mm"
                        format24h
                      >
                        <div class="row items-center justify-end">
                          <q-btn
                            v-close-popup
                            label="Close"
                            color="primary"
                            flat
                          />
                        </div>
                      </q-time>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>

            <div class="col-12">
              <Complete
                v-model="tmp.tags"
                :options="values.tags"
                canadd
                multiple
                label="Tags"
                @update:model-value="(newValue) => (tmp.tags = newValue)"
                @new-value="addNewValue"
              />
            </div>
            <div class="col-xs-12 col-sm-6">
              <Complete
                v-model="tmp.model"
                :options="values.model"
                label="Camera Model"
                @update:model-value="(newValue) => (tmp.model = newValue)"
              />
            </div>
            <div class="col-xs-12 col-sm-6">
              <Complete
                v-model="tmp.lens"
                :options="values.lens"
                label="Camera Lens"
                @update:model-value="(newValue) => (tmp.lens = newValue)"
              />
            </div>
            <div class="col-xs-6 col-sm-4">
              <q-input
                v-model="tmp.focal_length"
                type="number"
                label="Focal length"
              />
            </div>

            <div class="col-xs-6 col-sm-4">
              <q-input v-model="tmp.iso" type="number" label="ISO [ASA]" />
            </div>
            <div class="col-xs-6 col-sm-4">
              <q-input
                v-model="tmp.aperture"
                type="number"
                step="0.1"
                label="Aperture"
              />
            </div>
            <div class="col-xs-6 col-sm-4">
              <q-input v-model="tmp.shutter" label="Shutter [s]" />
            </div>

            <div class="col-xs-6 col-sm-4">
              <q-input
                v-model="tmp.loc"
                label="Location [latitude, longitude]"
                clearable
                clear-icon="clear"
              />
            </div>
            <div class="col-xs-6 col-sm-4 col-4 q-mt-sm">
              <q-checkbox v-model="tmp.flash" label="Flash fired?" />
            </div>
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { computed, ref } from "vue";
import { CONFIG, smallsized, readExif, formatBytes } from "../helpers";
import { useAppStore } from "../stores/app";
import { useAuthStore } from "../stores/auth";
import Complete from "./Complete.vue";

const emit = defineEmits(["edit-ok"]);
const props = defineProps({
  rec: Object,
});

const app = useAppStore();
const auth = useAuthStore();
const values = computed(() => app.values);
const tmp = ref({ ...props.rec });
const user = computed(() => auth.user);

const getExif = async () => {
  const exif = await readExif(tmp.value.filename);
  Object.keys(exif).forEach((k) => {
    tmp.value[k] = exif[k];
  });
  // add flash tag if exif flash true
  let tags = tmp.value.tags || [];
  if (tmp.value.flash && tags.indexOf("flash") === -1) {
    tags.push("flash");
  }
  tmp.value.tags = tags;
};
const addNewValue = (inputValue) => {
  tmp.value.tags.push(inputValue);
  app.values.tags.push(inputValue);
};

window.onpopstate = function () {
  app.showEdit = false;
};
const onCancel = () => {
  app.showEdit = false;
};
const onSubmit = () => {
  tmp.value.tags = tmp.value.tags ? tmp.value.tags : [];
  app.saveRecord(tmp.value);
  emit("edit-ok", tmp.value.id);
  app.showEdit = false;
};
</script>
