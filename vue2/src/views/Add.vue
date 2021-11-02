<template>
  <div>
    <Edit
      :visible="editForm"
      :current="current"
      @close="editForm = false"
    ></Edit>

    <v-container>
      <v-sheet class="mb-3 pa-3">
        <div
          class="d-flex flex-column justify-center"
          style="position: relative; height: 120px"
          :key="this.upload.status"
        >
          <template v-if="this.upload.status === code.INITIAL">
            <input
              type="file"
              multiple
              name="photos"
              @change="filesChange($event.target.name, $event.target.files)"
              accept=".jpg, .jpeg, image/jpeg"
              class="input-file"
            />
            <div class="subheading text-center">
              Drag your images here to upload, or click to browse.
              <br />Accepts only jpg (jpeg) files less then 4 Mb in size.
            </div>
          </template>
          <template v-if="this.upload.status === code.SAVING">
            <v-progress-linear
              v-model="this.upload.value"
              color="secondary"
              height="16"
              key="saving"
            ></v-progress-linear>
            <div class="subheading text-center">
              Upload in progress {{ this.upload.value }}%
            </div>
          </template>
          <template v-if="this.upload.status === code.PROCESSING">
            <v-progress-linear
              color="secondary"
              indeterminate
              height="16"
              key="processing"
            ></v-progress-linear>
            <div class="subheading text-center">
              Processing images. Please wait …
            </div>
          </template>
          <template v-if="this.upload.status === code.FAILED">
            <h3 class="text-h5">Upload failed</h3>
            <div class="subheading text-center error--text">
              Something went wrong.
            </div>
          </template>
        </div>
      </v-sheet>

      <template v-for="(item, k) in this.upload.failed">
        <v-alert
          dense
          dismissible
          class="mb-3"
          type="error"
          border="left"
          :key="k"
          >{{ item.filename }}, {{ formatBytes(item.size) }},
          {{ errors[item.error] }}</v-alert
        >
      </template>

      <v-sheet v-if="upload.list.length > 0">
        <v-slide-y-transition group tag="v-list">
          <template v-for="(item, j) in upload.list">
            <v-divider v-if="j !== 0" :key="`${j}-divider`"></v-divider>

            <v-list-item :key="j">
              <v-list-item-avatar>
                <img class="lazy" v-lazy="getImgSrc(item, 400)" />
              </v-list-item-avatar>

              <v-list-item-content>
                <v-list-item-title>{{ item.filename }}</v-list-item-title>
                <v-list-item-subtitle>{{
                  formatBytes(item.size)
                }}</v-list-item-subtitle>
              </v-list-item-content>

              <v-list-item-action class="d-flex flex-row">
                <v-btn color="error" class="mr-3" @click="removeRecord(item)">
                  <v-icon left>delete</v-icon>Delete
                </v-btn>
                <v-btn
                  color="primary"
                  class="mr-3"
                  @click.stop="showEditForm(item)"
                >
                  <v-icon left>publish</v-icon>Publish
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </template>
        </v-slide-y-transition>
      </v-sheet>
    </v-container>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import common from '../helpers/mixins'
import CONFIG from '../helpers/config'

const axios = Vue.axios

export default {
  name: 'Add',
  components: {
    Edit: () => import(/* webpackChunkName: "edit" */ '../components/Edit'),
  },
  mixins: [common],
  data: () => ({
    code: {
      INITIAL: 0,
      SAVING: 1,
      PROCESSING: 2,
      SUCCESS: 3,
      FAILED: 4,
    },
    current: {},
    editForm: false,
    errors: {
      0: 'Wrong file type',
      1: 'File too big',
      2: 'File failed',
    },
  }),
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['upload']),
  },
  methods: {
    reset () {
      this.$store.dispatch('app/setSnackbar', null)
      this.$store.dispatch('app/changeUploadStatus', this.code.INITIAL)
      this.$store.dispatch('app/setUploadPercentage', 0)
    },
    progress (event) {
      this.$store.dispatch(
        'app/setUploadPercentage',
        Math.round((event.loaded * 100) / event.total)
      )
    },
    save (formData) {
      this.$store.dispatch('app/changeUploadStatus', this.code.SAVING)
      this.$store.dispatch('app/setSnackbar', 'Uploading images …')
      let success = false
      axios
        .post('add', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: this.progress,
        })
        .then((x) => x.data) // list
        .then((x) =>
          x.map((item) => {
            if (item.success) {
              this.$store.dispatch('app/addUploaded', item.rec)
            } else {
              this.addFailed(item.rec, 2)
            }
          })
        )
        .then(() => {
          if (success) {
            this.$store.dispatch('app/setSnackbar', null)
          }
          this.$store.dispatch('app/changeUploadStatus', this.code.SUCCESS)
          this.reset()
        })
        .catch(() => {
          this.$store.dispatch('app/changeUploadStatus', this.code.FAILED)
          this.reset()
        })
    },
    filesChange (fieldName, fileList) {
      // https://scotch.io/tutorials/how-to-handle-file-uploads-in-vue-2
      const formData = new FormData()
      if (!fileList.length) return
      // Array.from(Array(5).keys()) = [0, 1, 2, 3, 4]
      // [...Array(5).keys()] = [0, 1, 2, 3, 4]
      Array.from(Array(fileList.length).keys()).map((x) => {
        if (fileList[x].type !== CONFIG.fileType) {
          this.addFailed(fileList[x], 0)
        } else if (fileList[x].size > CONFIG.fileSize) {
          this.addFailed(fileList[x], 1)
        } else {
          formData.append(fieldName, fileList[x], fileList[x].name)
        }
      })
      let i = 0
      // eslint-disable-next-line no-unused-vars
      for (let pair of formData.entries()) {
        i++
      }
      if (i > 0) this.save(formData)
    },
    showEditForm (rec) {
      rec.email = this.user.email
      rec.headline = 'No name'
      this.current = { ...rec }
      this.$store.dispatch('app/resetFailed')
      this.editForm = true
    },
    removeRecord (rec) {
      this.$store.dispatch('app/deleteRecord', rec)
    },
    addFailed (file, error) {
      this.$store.dispatch('app/addFailed', {
        filename: file.name,
        size: file.size,
        error: error,
      })
    },
  },
}
</script>
