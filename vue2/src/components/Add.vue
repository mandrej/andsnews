<template>
  <div class="page-container">
    <md-app>
      <md-app-toolbar class="md-primary">
        <span class="md-title">Add</span>
      </md-app-toolbar>

      <md-app-content>
        <!-- https://scotch.io/tutorials/how-to-handle-file-uploads-in-vue-2 -->
        <form novalidate v-if="isInitial || isSaving">
          <!-- <h1 class="md-title">Upload images</h1> -->
          <div class="dropboxxx">
            <md-empty-state v-if="isInitial"
              md-icon="cloud_upload"
              md-label="Upload images"
              md-description="Drag your image(s) here to begin or click to browse.">
              <input type="file" multiple :name="uploadFieldName" :disabled="isSaving" @change="filesChange($event.target.name, $event.target.files); fileCount = $event.target.files.length" accept="image/*" class="input-file">
            </md-empty-state>
            <md-empty-state v-if="isSaving"
              md-icon="file_upload"
              md-label="Uploading images"
              :md-description="`Uploading ${fileCount} images...`">
            </md-empty-state>
          </div>
        </form>

        <p v-if="isSuccess">
          <a href="javascript:void(0)" @click="reset()">Upload again</a>
        </p>

        <md-list v-for="item in uploaded" :key="item.safekey">
            <md-list-item>
              <md-avatar>
                <img :src="src(item)" :alt="item.slug">
              </md-avatar>
              <span class="md-list-item-text">{{item.headline}}</span>
              <md-button class="md-primary" @click="deleteRecord(item)">Delete</md-button>
              <router-link :to="{ name: 'edit', params: { id: item.safekey }}">
                <md-button class="md-primary">Edit</md-button>
              </router-link>
            </md-list-item>
          </md-list>
      </md-app-content>
    </md-app>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { HTTP } from '../../config/http'

const STATUS_INITIAL = 0
const STATUS_SAVING = 1
const STATUS_SUCCESS = 2
const STATUS_FAILED = 3

export default {
  name: 'Add',
  data: () => ({
    uploadedFiles: [],
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
.dropbox {
  outline: 1px dashed grey; /* the dash box */
  outline-offset: -10px;
  background: lightcyan;
  color: dimgray;
  padding: 10px 10px;
  // min-height: 200px; /* minimum height */
  position: relative;
  cursor: pointer;
}
.md-empty-state {
  max-width: 100%;
}
.input-file {
  opacity: 0; /* invisible but it's there! */
  width: 100%;
  height: 100%;
  position: absolute;
  cursor: pointer;
}

.dropbox:hover {
  background: lightblue; /* when mouse over to the drop zone, change color */
}

.dropbox p {
  font-size: 1.2em;
  text-align: center;
  padding: 50px 0;
}
</style>
