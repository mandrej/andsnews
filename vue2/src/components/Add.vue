<template>
  <v-app light>
    <v-toolbar app>
      <v-icon @click="$router.push({name: 'home'})">arrow_back</v-icon>
      <v-toolbar-title>Add</v-toolbar-title>
    </v-toolbar>

    <v-content>
      <!-- https://scotch.io/tutorials/how-to-handle-file-uploads-in-vue-2 -->
      <form novalidate v-if="isInitial || isSaving">
        <v-jumbotron color="grey lighten-2" v-if="isInitial">
          <input type="file" multiple :name="uploadFieldName" :disabled="isSaving" @change="filesChange($event.target.name, $event.target.files)" accept="image/*" class="input-file">
          <v-container fill-height>
            <v-layout column justify-center align-center>
              <v-icon x-large color="primary">cloud_upload</v-icon>
              <h3 class="headline">Upload images</h3>
              <span class="subheading">Drag your image(s) here to begin or click to browse.</span>
            </v-layout>
          </v-container>
        </v-jumbotron>

        <v-alert
          type="success"
          :value="isSaving"
          transition="scale-transition">
          Uploading {{fileCount}} images...
        </v-alert>
      </form>

      <v-list two-line>
        <v-list-tile avatar v-for="item in uploaded" :key="item.safekey">
          <v-list-tile-avatar>
            <img :src="src(item)" :alt="item.slug">
          </v-list-tile-avatar>
          <v-list-tile-content>
            <v-list-tile-title v-html="item.headline"></v-list-tile-title>
            <v-list-tile-sub-title>{{item.date}}</v-list-tile-sub-title>
          </v-list-tile-content>
          <v-list-tile-action>
            <v-layout row>
              <v-btn color="secondary" @click="deleteRecord(item)">Delete</v-btn>
              <v-btn color="primary" :to="{ name: 'edit', params: { id: item.safekey }}">Edit</v-btn>
            </v-layout>
          </v-list-tile-action>
        </v-list-tile>
      </v-list>

      <v-layout justify-center v-if="isSuccess">
        <v-btn color="primary" @click="reset">Upload again</v-btn>
      </v-layout>

    </v-content>
  </v-app>
</template>

<script>
import { mapState } from 'vuex'
import { HTTP } from '../../helpers/http'

const STATUS_INITIAL = 0
const STATUS_SAVING = 1
const STATUS_SUCCESS = 2
const STATUS_FAILED = 3

export default {
  name: 'Add',
  data: () => ({
    uploadedFiles: [],
    fileCount: 0,
    uploadError: null,
    currentStatus: null,
    uploadFieldName: 'photos'
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
      HTTP.post('photo/add', formData, {headers: {'Content-Type': 'multipart/form-data'}})
        .then(x => x.data) // list
        .then(x => x.map(
          item => {
            this.uploadedFiles.push(item.rec)
            this.currentStatus = STATUS_SUCCESS
            this.$store.dispatch('uploadList', item.rec)
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
    deleteRecord (rec) {
      this.$store.dispatch('deleteRecord', rec)
    },
    src (rec) {
      if (rec && rec.serving_url) {
        if (process.env.NODE_ENV === 'development') {
          return rec.serving_url.replace('http://localhost:8080/_ah', '/_ah') + '=s400'
        } else {
          return rec.serving_url + '=s400'
        }
      } else {
        return '/static/broken.svg'
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
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
