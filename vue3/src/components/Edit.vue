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
              <Complete
                v-model="tmp.email"
                :options="emailValues"
                canadd
                label="Author"
                hint="Existing member can add freind's photo and email"
                :rules="[
                  (val) => !!val || 'Email is missing',
                  (val) => isValidEmail(val),
                ]"
                @update:model-value="(newValue) => (tmp.email = newValue)"
                @new-value="addNewEmail"
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
                :options="tagValues"
                canadd
                multiple
                label="Tags"
                @update:model-value="(newValue) => (tmp.tags = newValue)"
                @new-value="addNewTag"
              />
            </div>
            <div class="col-xs-12 col-sm-6">
              <Complete
                v-model="tmp.model"
                :options="modelValues"
                canadd
                label="Camera Model"
                @update:model-value="(newValue) => (tmp.model = newValue)"
                @new-value="addNewModel"
              />
            </div>
            <div class="col-xs-12 col-sm-6">
              <Complete
                v-model="tmp.lens"
                :options="lensValues"
                canadd
                label="Camera Lens"
                @update:model-value="(newValue) => (tmp.lens = newValue)"
                @new-value="addNewLens"
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
import { computed, reactive } from "vue";
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
const tagValues = computed(() => app.tagValues);
const emailValues = computed(() => app.emailValues);
const modelValues = computed(() => app.modelValues);
const lensValues = computed(() => app.lensValues);
const tmp = reactive({ ...props.rec });
const user = computed(() => auth.user);

const getExif = async () => {
  const exif = await readExif(tmp.filename);
  Object.keys(exif).forEach((k) => {
    tmp[k] = exif[k];
  });
  // add flash tag if exif flash true
  let tags = tmp.tags || [];
  if (tmp.flash && tags.indexOf("flash") === -1) {
    tags.push("flash");
  }
  tmp.tags = tags;
  tmp.email = user.value.email;
};
const isValidEmail = (val) => {
  const emailPattern =
    /^(?=[a-zA-Z0-9@._%+-]{6,254}$)[a-zA-Z0-9._%+-]{1,64}@(?:[a-zA-Z0-9-]{1,63}\.){1,8}[a-zA-Z]{2,63}$/;
  return emailPattern.test(val) || "Invalid email";
};

// new values
const addNewEmail = (inputValue) => {
  tmp.email = inputValue;
  app.values.email.push({
    count: 1,
    value: inputValue,
  });
};
const addNewTag = (inputValue) => {
  tmp.tags.push(inputValue);
  app.values.tags.push({
    count: 1,
    value: inputValue,
  });
};
const addNewModel = (inputValue) => {
  tmp.model.push(inputValue);
  app.values.model.push({
    count: 1,
    value: inputValue,
  });
};
const addNewLens = (inputValue) => {
  tmp.lens.push(inputValue);
  app.values.lens.push({
    count: 1,
    value: inputValue,
  });
};

window.onpopstate = function () {
  app.showEdit = false;
};
const onCancel = () => {
  app.showEdit = false;
};
const onSubmit = () => {
  tmp.tags = tmp.tags ? tmp.tags : [];
  app.saveRecord(tmp);
  emit("edit-ok", tmp.id);
  app.showEdit = false;
};
</script>
