<template>
  <div>
    <Edit :visible="editdForm" @close="editdForm = false"></Edit>

    <v-snackbar
      v-model="snackbar"
      :timeout="timeout"
      left
      bottom>
      Uploading {{fileCount}} images…
      <v-btn flat icon color="white" @click.native="snackbar = false">
        <v-icon>close</v-icon>
      </v-btn>
    </v-snackbar>

    <v-dialog
      v-model="show"
      lazy
      fullscreen
      transition="dialog-bottom-transition"
      hide-overlay
      scrollable>
      <v-card tile light>
        <v-toolbar card>
          <v-btn icon @click.native="show = false">
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title>Add</v-toolbar-title>
        </v-toolbar>
        <!-- https://scotch.io/tutorials/how-to-handle-file-uploads-in-vue-2 -->
        <form novalidate v-if="isInitial || isSaving">
          <v-jumbotron color="grey lighten-2" v-if="isInitial">
            <input type="file"
              multiple
              :name="uploadFieldName"
              :disabled="isSaving"
              @change="filesChange($event.target.name, $event.target.files)"
              accept="image/*"
              class="input-file">
            <v-container fill-height>
              <v-layout column justify-center align-center>
                <v-icon x-large color="primary">cloud_upload</v-icon>
                <h3 class="headline">Upload images</h3>
                <span class="subheading">Drag your image(s) here to begin or click to browse.</span>
              </v-layout>
            </v-container>
          </v-jumbotron>
        </form>

        <v-card-text>
          <v-list two-line>
            <v-list-tile avatar v-for="item in uploaded" :key="item.safekey">
              <v-list-tile-avatar>
                <img :src="getImgSrc(item, 's')" :alt="item.slug">
              </v-list-tile-avatar>
              <v-list-tile-content>
                <v-list-tile-title>{{item.headline}}</v-list-tile-title>
                <v-list-tile-sub-title>{{dateFormat(item)}}</v-list-tile-sub-title>
              </v-list-tile-content>
              <v-list-tile-action>
                <v-layout row>
                  <v-btn color="error" @click="removeRecord(item)">Delete</v-btn>&nbsp;
                  <v-btn color="primary" @click="showEditdForm(item)">Edit</v-btn>
                </v-layout>
              </v-list-tile-action>
            </v-list-tile>
          </v-list>

          <v-layout justify-center v-if="isSuccess">
            <v-btn @click="reset">Upload again</v-btn>
          </v-layout>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { HTTP } from '../../helpers/http'
import common from '../../helpers/mixins'
import Edit from './Edit'

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
    editdForm: false,
    snackbar: false,
    timeout: 3000
  }),
  mounted () {
    this.reset()
  },
  computed: {
    ...mapState(['uploaded']),
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
      // reset form to initial state
      this.currentStatus = STATUS_INITIAL
      this.uploadedFiles = []
      this.uploadError = null
    },
    save (formData) {
      // upload data to the server
      this.currentStatus = STATUS_SAVING
      this.snackbar = true
      HTTP.post('photo/add', formData, {headers: {'Content-Type': 'multipart/form-data'}})
        .then(x => x.data) // list
        .then(x => x.map(
          item => {
            this.uploadedFiles.push(item.rec)
            this.currentStatus = STATUS_SUCCESS
            this.$store.dispatch('addUploaded', item.rec)
            this.$store.dispatch('addRecord', item.rec)
          }
        ))
        .catch(err => {
          this.uploadError = err.response
          this.currentStatus = STATUS_FAILED
        })
    },
    filesChange (fieldName, fileList) {
      // handle file changes
      this.fileCount = fileList.length
      const formData = new FormData()
      if (!fileList.length) return

      Array
        .from(Array(fileList.length).keys())
        .map(x => {
          formData.append(fieldName, fileList[x], fileList[x].name)
        })
      // save it
      this.save(formData)
    },
    showEditdForm (rec) {
      this.$store.dispatch('changeCurrent', rec)
      this.editdForm = true
    },
    removeRecord (rec) {
      this.$store.dispatch('deleteRecord', rec)
    }
  }
}
</script>

<style lang="scss" scoped>
.jumbotron {
  height: 200px !important;
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
