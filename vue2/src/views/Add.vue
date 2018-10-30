<template>
  <div>
    <Edit :visible="editForm" @close="editForm = false"></Edit>

    <v-snackbar
      v-model="snackbar"
      :timeout="timeout"
      left bottom>
      Uploading {{fileCount}} images…
      <v-btn flat icon color="white" @click="snackbar = false">
        <v-icon>close</v-icon>
      </v-btn>
    </v-snackbar>

    <v-app>
      <v-toolbar app light class="aperture">
        <v-btn icon @click="$router.push({ name: 'home' })">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <v-toolbar-title class="headline">Add</v-toolbar-title>
      </v-toolbar>

      <v-content>
        <v-container>
          <v-responsive height="120px" class="mb-3">
            <input type="file" multiple
              :name="uploadFieldName"
              :disabled="isSaving"
              @change="filesChange($event.target.name, $event.target.files)"
              accept="image/*"
              class="input-file">
            <v-container fill-height>
              <v-layout column justify-center align-center>
                <template v-if="isInitial">
                  <h3 class="headline">Upload images <v-icon large>cloud_upload</v-icon></h3>
                  <span class="subheading text-xs-center">Drag your images here to upload, or click to browse.</span>
                </template>
                <template v-if="isSaving">
                  <v-progress-linear
                    :active="true"
                    :query="value < 100"
                    :indeterminate="value === 100"
                    color="secondary"
                    v-model="value"></v-progress-linear>
                  <span v-if="value < 100" class="subheading text-xs-center">Upload in progress {{value}}%.</span>
                  <span v-if="value === 100" class="subheading text-xs-center">Progressing images. Please wait</span>
                </template>
                <template v-if="isFailed">
                  <h3 class="headline">Upload failed</h3>
                  <span v-if="isFailed" class="subheading text-xs-center error--text">Something went wrong.</span>
                </template>
              </v-layout>
            </v-container>
          </v-responsive>

          <v-slide-y-transition v-if="uploaded.length > 0" hide-on-leave group tag="v-list" two-line>
            <template v-for="(item, i) in uploaded">
              <v-divider v-if="i !== 0" :key="`${i}-divider`"></v-divider>
              <v-list-tile avatar :key="item.safekey">
                <v-list-tile-avatar>
                  <img :src="getImgSrc(item, '400')" :alt="item.slug">
                </v-list-tile-avatar>
                <v-list-tile-content>
                  <v-list-tile-title>{{item.headline}}</v-list-tile-title>
                  <v-list-tile-sub-title>{{dateFormat(item)}}</v-list-tile-sub-title>
                </v-list-tile-content>
                <v-list-tile-action>
                  <v-layout row>
                    <v-btn color="error" @click="removeRecord(item)">Delete</v-btn>&nbsp;
                    <v-btn color="secondary" @click="showEditForm(item)">Edit</v-btn>
                  </v-layout>
                </v-list-tile-action>
              </v-list-tile>
            </template>
          </v-slide-y-transition>

        </v-container>
      </v-content>

      <Footer/>
    </v-app>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

const axios = Vue.axios

const STATUS_INITIAL = 0
const STATUS_SAVING = 1
const STATUS_SUCCESS = 2
const STATUS_FAILED = 3

export default {
  name: 'Add',
  props: ['visible'],
  components: {
    'Edit': () => import(/* webpackChunkName: "edit" */ '@/components/Edit'),
    'Footer': () => import(/* webpackChunkName: "footer" */ '@/components/Footer')
  },
  mixins: [ common ],
  data: () => ({
    uploadedFiles: [],
    fileCount: 0,
    uploadError: null,
    currentStatus: null,
    uploadFieldName: 'photos',
    editForm: false,
    snackbar: false,
    timeout: 0,
    value: 0
  }),
  mounted () {
    this.reset()
  },
  computed: {
    ...mapState('app', ['uploaded']),
    isInitial () {
      return this.currentStatus === STATUS_INITIAL
    },
    isSaving () {
      return this.currentStatus === STATUS_SAVING
    },
    isSuccess () {
      return this.currentStatus === STATUS_SUCCESS
    },
    isFailed () {
      return this.currentStatus === STATUS_FAILED
    }
  },
  methods: {
    reset () {
      this.currentStatus = STATUS_INITIAL
      this.uploadedFiles = []
      this.uploadError = null
      this.value = 0
    },
    progress (event) {
      this.value = Math.round((event.loaded * 100) / event.total)
    },
    save (formData) {
      this.currentStatus = STATUS_SAVING
      this.snackbar = true
      axios.post('photo/add', formData, {headers: {'Content-Type': 'multipart/form-data'}, onUploadProgress: this.progress})
        .then(x => x.data) // list
        .then(x => x.map(
          item => {
            this.uploadedFiles.push(item.rec)
            this.$store.dispatch('app/addRecord', item.rec)
          }
        ))
        .then(() => {
          this.snackbar = false
          this.currentStatus = STATUS_SUCCESS
          this.reset()
        })
        .catch(err => {
          this.uploadError = err.response
          this.currentStatus = STATUS_FAILED
        })
    },
    filesChange (fieldName, fileList) {
      // https://scotch.io/tutorials/how-to-handle-file-uploads-in-vue-2
      this.fileCount = fileList.length
      const formData = new FormData()
      if (!fileList.length) return

      // make formData
      Array
        .from(Array(fileList.length).keys())
        .map(x => {
          formData.append(fieldName, fileList[x], fileList[x].name)
        })
      this.save(formData)
    },
    showEditForm (rec) {
      this.$store.dispatch('app/changeCurrent', rec)
      this.editForm = true
    },
    removeRecord (rec) {
      this.$store.dispatch('app/deleteRecord', rec)
    }
  }
}
</script>

<style scoped>
.v-responsive {
  outline: 2px dashed #BDBDBD;
  cursor: pointer;
}
.input-file {
  opacity: 0; /* invisible but it's there! */
  width: 100%;
  height: 100%;
  position: absolute;
  cursor: pointer;
}
</style>
