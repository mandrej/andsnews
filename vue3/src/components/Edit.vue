<template>
  <q-dialog
    ref="dialogRef"
    @hide="onDialogHide"
    transition-show="slide-down"
    transition-hide="slide-up"
    :maximized="$q.screen.lt.md"
    persistent
  >
    <q-card class="q-dialog-plugin full-width" style="max-width: 800px">
      <q-toolbar class="bg-grey-2 text-black row justify-between" bordered>
        <div>
          <q-btn flat round dense icon="close" @click="onCancelClick" />
          <q-btn class="gt-sm" v-if="user.isAdmin" flat label="Read Exif" @click="getExif" />
        </div>
        <div>{{ humanStorageSize(tmp.size) }} {{ linearDim(tmp) }}</div>
        <q-btn color="primary" label="Submit" @click="onOKClick" />
      </q-toolbar>
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
            <Complete
              :modelValue="tmp.tags"
              :options="values.tags"
              canadd
              multiple
              label="Tags"
              @update:model-value="newValue => tmp.tags = newValue"
            />
          </div>
          <div class="col-xs-12 col-sm-6">
            <Complete
              :modelValue="tmp.model"
              :options="values.model"
              label="Camera Model"
              @update:model-value="newValue => tmp.model = newValue"
            />
          </div>
          <div class="col-xs-12 col-sm-6">
            <Complete
              :modelValue="tmp.lens"
              :options="values.lens"
              label="Camera Lens"
              @update:model-value="newValue => tmp.lens = newValue"
            />
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
import { computed, onMounted, reactive, toRefs } from "vue";
import { useDialogPluginComponent } from 'quasar'
import { smallsized, readExif } from "../helpers"
import { useStore } from "vuex";
import Complete from './Complete.vue';

const { humanStorageSize } = format

export default {
  name: "Edit",
  props: { rec: Object },
  components: {
    Complete
  },
  emits: [
    ...useDialogPluginComponent.emits
  ],
  setup(props) {
    let tmp = reactive({ ...props.rec });
    console.log(tmp);
    const store = useStore();
    const values = computed(() => store.state.app.values)
    const linearDim = (rec) => {
      const dim = rec.dim || []
      return dim.join('✕') || ''
    }
    const getExif = async () => {
      const exif = await readExif(tmp.filename);
      Object.keys(exif).forEach(k => {
        tmp[k] = exif[k]
      })
      // add flash tag if exif flash true
      let tags = tmp.tags || []
      if (tmp.flash && tags.indexOf('flash') === -1) {
        tags.push('flash')
      }
      tmp.tags = tags
    }
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()


    onMounted(() => {
      window.onpopstate = function () {
        onDialogCancel()
      }
    })
    const onCancelClick = () => {
      window.history.back()
      return onDialogCancel()
    }
    const onOKClick = () => {
      tmp.tags = tmp.tags ? tmp.tags : []
      store.dispatch('app/saveRecord', { ...tmp })
      onDialogOK()
    }

    return {
      tmp,
      close,
      linearDim,
      humanStorageSize,
      getExif,
      smallsized,
      values,
      dialogRef,
      user: computed(() => store.state.auth.user),

      onDialogHide,
      onOKClick,
      onCancelClick,
    };
  },
}
</script>
