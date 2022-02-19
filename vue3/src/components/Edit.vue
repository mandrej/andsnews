<template>
  <q-dialog
    ref="dialogRef"
    @hide="onDialogHide"
    transition-show="slide-up"
    transition-hide="slide-down"
    persistent
  >
    <q-card class="q-dialog-plugin full-width" style="max-width: 800px">
      <q-card-actions class="row justify-between q-pa-md q-col-gutter-md">
        <div class="col">
          <q-btn class="q-mr-md" color="primary" label="Submit" @click="onOKClick" />
          <q-btn v-if="user.isAdmin" flat label="Read Exif" @click="readExif" />
        </div>
        <div class="col text-right">
          <span class="q-pr-md">{{ humanStorageSize(tmp.size) }} {{ linearDim(tmp) }}</span>
          <q-btn icon="close" flat round @click="onCancelClick" />
        </div>
      </q-card-actions>
      <q-separator />
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-xs-12 col-sm-4 gt-xs">
            <q-img :src="smallsized + tmp.filename" :ratio="1" />
          </div>
          <div class="col-xs-12 col-sm-8 col-8">
            <q-input
              v-model="tmp.headline"
              label="Headline"
              :rules="[
                val => !!val || '* Required',
              ]"
              lazy-rules
            />
            <q-input v-model="tmp.filename" label="Filename" readonly />
            <q-select v-model="tmp.email" :options="values.email" label="Author"></q-select>
            <q-input v-model="tmp.date" label="Date taken">
              <template v-slot:prepend>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="tmp.date" mask="YYYY-MM-DD HH:mm">
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
              <template v-slot:append>
                <q-icon name="access_time" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-time v-model="tmp.date" mask="YYYY-MM-DD HH:mm" format24h>
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-time>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </div>

          <div class="col-12">
            <q-select
              v-model="tmp.tags"
              :options="values.tags"
              use-input
              use-chips
              multiple
              hide-dropdown-icon
              input-debounce="0"
              new-value-mode="add-unique"
              label="Tags"
            >
              <template v-slot:append>
                <q-icon
                  v-if="tmp.tags && tmp.tags.length !== 0"
                  class="cursor-pointer"
                  name="clear"
                  @click.stop="tmp.tags = []"
                />
              </template>
            </q-select>
          </div>

          <div class="col-xs-12 col-sm-6">
            <q-select v-model="tmp.model" :options="values.model" label="Camera Model" />
          </div>
          <div class="col-xs-12 col-sm-6">
            <q-select v-model="tmp.lens" :options="values.lens" label="Lens" />
          </div>
          <div class="col-xs-6 col-sm-4">
            <q-input v-model="tmp.focal_length" type="number" label="Focal length" />
          </div>

          <div class="col-xs-6 col-sm-4">
            <q-input v-model="tmp.iso" type="number" label="ISO [ASA]" />
          </div>
          <div class="col-xs-6 col-sm-4">
            <q-input v-model="tmp.aperture" type="number" step="0.1" label="Aperture" />
          </div>
          <div class="col-xs-6 col-sm-4">
            <q-input v-model="tmp.shutter" label="Shutter [s]" />
          </div>

          <div class="col-xs-6 col-sm-4">
            <q-input v-model="tmp.loc" label="Location [latitude, longitude]" />
          </div>
          <div class="col-xs-6 col-sm-4 col-4 q-mt-sm">
            <q-checkbox v-model="tmp.flash" label="Flash fired?" />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script>
import { format } from 'quasar'
import { defineComponent, computed, ref, onMounted } from "vue";
import { useDialogPluginComponent } from 'quasar'
import { api, smallsized } from "../helpers"
import { useStore } from "vuex";

const { humanStorageSize } = format

export default defineComponent({
  name: "Edit",
  props: { rec: Object },
  emits: [
    ...useDialogPluginComponent.emits
  ],
  setup(props) {
    const store = useStore();
    const tmp = ref({ ...props.rec });
    const values = computed(() => store.state.app.values)
    const linearDim = (rec) => {
      const dimension = rec.dim || []
      return dimension.join('✕') || ''
    }
    const readExif = () => {
      api.get('exif/' + tmp.value.filename).then((response) => {
        tmp.value = { ...tmp.value, ...response.data }
        // add flash tag if exif flash true
        let tags = tmp.value.tags || []
        if (response.data.flash && tags.indexOf('flash') === -1) {
          tags.push('flash')
          tmp.value = { ...tmp.value, ...{ tags: tags } }
        }
      })
    }
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

    onMounted(() => {
      if (!tmp.value.date) {
        readExif()
      }
    })

    return {
      tmp,
      linearDim,
      humanStorageSize,
      readExif,
      smallsized,
      values,
      dialogRef,
      onDialogHide,
      user: computed(() => store.state.auth.user),

      onOKClick() {
        tmp.value.tags = tmp.value.tags ? tmp.value.tags : []
        store.dispatch('app/saveRecord', tmp.value)
        onDialogOK()
      },
      onCancelClick: onDialogCancel
    };
  },
});
</script>
