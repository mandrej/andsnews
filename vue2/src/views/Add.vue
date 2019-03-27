<template>
  <div>
    <Edit :visible="editForm" :rec="current" @close="editForm = false"></Edit>

    <v-snackbar left bottom
      v-model="snackbar"
      :timeout="timeout">
      {{ message }}
      <v-btn flat icon color="white" @click="snackbar = false">
        <v-icon>close</v-icon>
      </v-btn>
    </v-snackbar>

    <v-app>
      <v-toolbar app flat light class="aperture">
        <v-btn icon @click="$router.go(-1)">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <v-toolbar-title class="headline">Add</v-toolbar-title>
      </v-toolbar>

      <v-content class="aperture">
        <v-container>
          <v-responsive height="120px" class="mb-3">
            <input type="file" multiple
              name="photos"
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
                  <span v-if="value === 100" class="subheading text-xs-center">Processing images. Please wait</span>
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
                  <img :src="getImgSrc(item, '400-c')" :alt="item.slug">
                </v-list-tile-avatar>
                <v-list-tile-content>
                  <v-list-tile-title>{{item.headline}}</v-list-tile-title>
                  <v-list-tile-sub-title>{{formatDate(item.date)}}</v-list-tile-sub-title>
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
    </v-app>
  </div>
</template>

<script>
import Vue from 'vue'
import { EventBus } from '@/helpers/event-bus'
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

const axios = Vue.axios

const STATUS_INITIAL = 0
const STATUS_SAVING = 1
const STATUS_SUCCESS = 2
const STATUS_FAILED = 3

export default {
  name: 'Add',
  components: {
    'Edit': () => import(/* webpackChunkName: "edit" */ '@/components/Edit')
  },
  mixins: [ common ],
  data: () => ({
    current: {},
    uploadedFiles: [],
    fileCount: 0,
    uploadError: null,
    status: null,
    editForm: false,
    value: 0,
    snackbar: false,
    timeout: 0,
    message: ''
  }),
  mounted () {
    EventBus.$on('delete', message => {
      this.message = message
      this.timeout = 6000
      this.snackbar = true
    })
    this.reset()
  },
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['uploaded']),
    isInitial () {
      return this.status === STATUS_INITIAL
    },
    isSaving () {
      return this.status === STATUS_SAVING
    },
    isSuccess () {
      return this.status === STATUS_SUCCESS
    },
    isFailed () {
      return this.status === STATUS_FAILED
    }
  },
  methods: {
    reset () {
      this.status = STATUS_INITIAL
      this.uploadedFiles = []
      this.uploadError = null
      this.value = 0
    },
    progress (event) {
      this.value = Math.round((event.loaded * 100) / event.total)
    },
    save (formData) {
      this.status = STATUS_SAVING
      this.message = 'Uploading ' + this.fileCount + ' images…'
      this.timeout = 0
      this.snackbar = true
      axios.post('add', formData, { headers: { 'Content-Type': 'multipart/form-data' }, onUploadProgress: this.progress })
        .then(x => x.data) // list
        .then(x => x.map(
          item => {
            this.uploadedFiles.push(item.rec)
            this.$store.dispatch('app/addRecord', item.rec)
          }
        ))
        .then(() => {
          this.snackbar = false
          this.status = STATUS_SUCCESS
          this.reset()
        })
        .catch(err => {
          this.uploadError = err.response
          this.status = STATUS_FAILED
        })
    },
    filesChange (fieldName, fileList) {
      // https://scotch.io/tutorials/how-to-handle-file-uploads-in-vue-2
      this.fileCount = fileList.length
      const formData = new FormData()
      if (!fileList.length) return
      formData.append('email', this.user.email)

      // make formData from Array Iterator
      // Array.from(Array(5).keys()) = [0, 1, 2, 3, 4]
      // [...Array(5).keys()] = [0, 1, 2, 3, 4]
      // eslint-disable-next-line
      // File(531551) {name: "jutro2.jpg", lastModified: 1538385671886, lastModifiedDate: Mon Oct 01 2018 11..., size: 531551, type: "image/jpeg"
      Array
        .from(Array(fileList.length).keys())
        .map(x => {
          formData.append(fieldName, fileList[x], fileList[x].name)
        })
      this.save(formData)
    },
    showEditForm (rec) {
      this.current = rec
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
  outline: 2px dashed #37474F;
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
