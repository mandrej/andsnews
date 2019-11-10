<template>
  <div>
    <Edit :visible="editForm" :rec="current" @close="editForm = false"></Edit>

    <Message :model="snackbar" :message="message" @update-snackbar="updateSnackbar"></Message>

    <v-app>
      <v-app-bar app light>
        <v-btn icon @click="$router.go(-1)">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <v-img src="/static/img/aperture.svg" max-height="40" max-width="40" class="mr-3"></v-img>
        <v-toolbar-title class="headline">Add</v-toolbar-title>
      </v-app-bar>

      <v-content>
        <v-container mt-4>
          <div class="dotted mb-3 pa-4">
            <v-layout column justify-center align-center style="height: 120px">
              <template v-if="isInitial">
                <input
                  type="file"
                  multiple
                  name="photos"
                  @change="filesChange($event.target.name, $event.target.files)"
                  accept="image/*"
                  class="input-file"
                />
                <h3 class="headline">Upload images</h3>
                <div
                  class="subheading text-center"
                >Drag your images here to upload, or click to browse</div>
              </template>
              <template v-if="isSaving">
                <v-progress-linear
                  :active="true"
                  :query="value < 100"
                  :indeterminate="value === 100"
                  height="16"
                  color="secondary"
                  striped
                  v-model="value"
                ></v-progress-linear>
                <div v-if="value < 100" class="subheading text-center">Upload in progress {{value}}%</div>
                <div
                  v-else-if="value === 100"
                  class="subheading text-center"
                >Processing images. Please wait …</div>
              </template>
              <template v-if="isFailed">
                <h3 class="headline">Upload failed</h3>
                <div class="subheading text-center error--text">Something went wrong.</div>
              </template>
            </v-layout>
          </div>

          <v-list v-if="uploaded.length > 0" two-line>
            <template v-for="(item, i) in uploaded">
              <v-divider v-if="i !== 0" :key="`${i}-divider`"></v-divider>
              <v-list-item :key="i">
                <v-list-item-avatar>
                  <img :src="getImgSrc(item, '400-c')" :alt="item.slug" />
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title>{{item.headline}}</v-list-item-title>
                  <v-list-item-subtitle>{{formatDate(item.date)}}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-layout row>
                    <v-btn class="mr-3" color="error" @click="removeRecord(item)">Delete</v-btn>
                    <v-btn color="primary" @click="showEditForm(item)">Edit</v-btn>
                  </v-layout>
                </v-list-item-action>
              </v-list-item>
            </template>
          </v-list>
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
    'Edit': () => import(/* webpackChunkName: "edit" */ '@/components/Edit'),
    'Message': () => import(/* webpackChunkName: "message" */ '@/components/Message')
  },
  mixins: [common],
  data: () => ({
    current: {},
    uploadedFiles: [],
    fileCount: 0,
    status: null,
    editForm: false,
    value: 0,
    snackbar: false,
    message: ''
  }),
  mounted () {
    EventBus.$on('delete', message => {
      this.message = message
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
      this.value = 0
    },
    progress (event) {
      this.value = Math.round((event.loaded * 100) / event.total)
    },
    save (formData) {
      this.status = STATUS_SAVING
      this.message = 'Uploading ' + this.fileCount + ' images …'
      this.snackbar = true
      let success = false
      axios.post('add', formData, { headers: { 'Content-Type': 'multipart/form-data' }, onUploadProgress: this.progress })
        .then(x => x.data) // list
        .then(x => x.map(
          item => {
            success = item.success
            if (success) {
              this.uploadedFiles.push(item.rec)
              this.$store.dispatch('app/addRecord', item.rec)
            } else {
              this.message = item.message
            }
          }
        ))
        .then(() => {
          if (success) this.snackbar = false
          this.status = STATUS_SUCCESS
          this.reset()
        })
        .catch(err => {
          this.message = err.response
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
