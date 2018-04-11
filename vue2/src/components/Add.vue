<template>
  <div class="page-container">
    <md-app>
      <md-app-toolbar class="md-primary">
        <span class="md-title">Add</span>
      </md-app-toolbar>

      <md-app-content>
        <!-- https://scotch.io/tutorials/how-to-handle-file-uploads-in-vue-2 -->
        <form enctype="multipart/form-data" novalidate v-if="isInitial || isSaving">
          <h1>Upload images</h1>
          <div class="dropbox">
            <input type="file" multiple :name="uploadFieldName" :disabled="isSaving" @change="filesChange($event.target.name, $event.target.files); fileCount = $event.target.files.length" accept="image/*" class="input-file">
            <p v-if="isInitial">
              Drag your file(s) here to begin<br> or click to browse
            </p>
            <p v-if="isSaving">
              Uploading {{ fileCount }} files...
            </p>
          </div>
        </form>
      </md-app-content>
    </md-app>
  </div>
</template>

<script>
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
    upload (formData) {
      // HTTP.post('photo/add', {content: formData}, {headers: {'Content-Type': 'multipart/form-data'}})
      HTTP.post('photo/add', formData)
        .then(x => x.data) // list
        .then(x => x.map(
          // item => Object.assign({}, item.rec, {url: `${item.rec.filename}`})
          item => {
            console.log(item.rec)
            this.uploadedFiles.push(item.rec)
            this.currentStatus = STATUS_SUCCESS
          }
        ))
        .catch(err => {
          this.uploadError = err.response
          this.currentStatus = STATUS_FAILED
        })
    },
    save (formData) {
      // upload data to the server
      this.currentStatus = STATUS_SAVING

      this.upload(formData)
      // doesn't wait !!!
      this.$store.dispatch('uploadList', this.uploadedFiles)

      // .then(x => console.log(x))
      // .then(rec => {
      //   this.uploadedFiles = [].concat(rec)
      //   this.currentStatus = STATUS_SUCCESS
      //   // this.$store.dispatch('uploadList', rec)
      // })
      // .catch(err => {
      //   this.uploadError = err.response
      //   this.currentStatus = STATUS_FAILED
      // })
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
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.dropbox {
  outline: 2px dashed grey; /* the dash box */
  outline-offset: -10px;
  background: lightcyan;
  color: dimgray;
  padding: 10px 10px;
  min-height: 200px; /* minimum height */
  position: relative;
  cursor: pointer;
}
.input-file {
  opacity: 0; /* invisible but it's there! */
  width: 100%;
  height: 200px;
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
