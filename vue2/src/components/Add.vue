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

    <v-dialog
      v-model="show"
      lazy fullscreen hide-overlay scrollable
      transition="dialog-bottom-transition">
      <v-card tile light>
        <v-toolbar light class="aperture">
          <v-btn icon @click="show = false">
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title class="headline">Add</v-toolbar-title>
        </v-toolbar>
        <v-card-text>
          <v-container>
            <!-- https://scotch.io/tutorials/how-to-handle-file-uploads-in-vue-2 -->
            <v-responsive height="200px" v-if="isInitial || isSaving || isFailed">
              <input type="file" multiple
                :name="uploadFieldName"
                :disabled="isSaving"
                @change="filesChange($event.target.name, $event.target.files)"
                accept="image/*"
                class="input-file">
              <v-container fill-height>
                <v-layout column justify-center align-center>
                  <v-progress-circular v-if="isSaving"
                    :size="100"
                    :width="5"
                    :rotate="-90"
                    :value="value"
                    color="secondary">{{value}}</v-progress-circular>
                  <h3 class="headline">Upload images</h3>
                  <span v-if="isInitial" class="subheading">Drag your image(s) here to begin or click to browse.</span>
                  <span v-if="isFailed" class="subheading error--text">Upload failed.</span>
                </v-layout>
              </v-container>
            </v-responsive>

            <v-list two-line>
              <v-list-tile avatar v-for="item in uploaded" :key="item.safekey">
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
            </v-list>

            <v-layout justify-center v-if="isSuccess">
              <v-btn @click="reset">Upload again</v-btn>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import common from '@/helpers/mixins'
import Edit from './Edit'

const axios = Vue.axios

const STATUS_INITIAL = 0
const STATUS_SAVING = 1
const STATUS_SUCCESS = 2
const STATUS_FAILED = 3

export default {
  name: 'Add',
  props: ['visible'],
  components: {
    Edit
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
    ...mapState('All', ['uploaded']),
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
            this.$store.dispatch('All/addRecord', item.rec)
          }
        ))
        .then(() => {
          this.snackbar = false
          this.currentStatus = STATUS_SUCCESS
        })
        .catch(err => {
          this.uploadError = err.response
          this.currentStatus = STATUS_FAILED
        })
    },
    filesChange (fieldName, fileList) {
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
      this.$store.dispatch('All/changeCurrent', rec)
      this.editForm = true
    },
    removeRecord (rec) {
      this.$store.dispatch('All/deleteRecord', rec)
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
