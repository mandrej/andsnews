<template>
  <v-dialog
    v-model="show"
    persistent
    max-width="800"
    :fullscreen="$vuetify.breakpoint.xsOnly"
    @keydown.esc="show = false"
    transition="dialog-bottom-transition"
  >
    <v-card>
      <v-app-bar>
        <v-btn color="primary" @click="submit" :disabled="!valid">Submit</v-btn>
        <v-btn color="ml-2" if="user.isAdmin" @click="readExif"
          >Read Exif</v-btn
        >
        <v-spacer></v-spacer>
        <span class="pr-4 hidden-sm-and-down"
          >{{ formatBytes(tmp.size) }} {{ linearDim }}</span
        >
        <v-btn icon @click="show = false">
          <v-icon>close</v-icon>
        </v-btn>
      </v-app-bar>
      <v-card-text class="pt-6">
        <v-form>
          <v-row>
            <v-col cols="12" md="4" sm="4">
              <v-img
                aspect-ratio="1"
                :src="
                  !tmp.date
                    ? fullsized + tmp.filename
                    : smallsized + tmp.filename
                "
                class="d-none d-sm-flex"
              ></v-img>
            </v-col>
            <v-col cols="12" md="8" sm="8">
              <v-text-field
                v-model="tmp.headline"
                :rules="requiredRule"
                :label="`Headline for ${tmp.filename}`"
                :dense="$vuetify.breakpoint.xsOnly"
                required
              ></v-text-field>
              <v-autocomplete
                v-model="tmp.email"
                :items="values.email"
                label="Author"
              ></v-autocomplete>
              <v-row>
                <v-col cols="6" md="6" sm="6">
                  <v-menu
                    v-model="menuDate"
                    ref="dateRef"
                    :close-on-content-click="false"
                    :return-value.sync="dateTime.date"
                    transition="scale-transition"
                    offset-y
                    min-width="auto"
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-text-field
                        v-model="dateTime.date"
                        label="Date taken"
                        prepend-icon="event"
                        readonly
                        v-bind="attrs"
                        v-on="on"
                      ></v-text-field>
                    </template>
                    <v-date-picker
                      color="primary"
                      v-model="dateTime.date"
                      scrollable
                    >
                      <v-spacer></v-spacer>
                      <v-btn text @click="dateRef = false">Cancel</v-btn>
                      <v-btn text @click="$refs.dateRef.save(dateTime.date)"
                        >OK</v-btn
                      >
                    </v-date-picker>
                  </v-menu>
                </v-col>
                <v-col cols="6" md="6" sm="6">
                  <v-menu
                    v-model="menuTime"
                    ref="timeRef"
                    :close-on-content-click="false"
                    :nudge-right="40"
                    :return-value.sync="dateTime.time"
                    transition="scale-transition"
                    offset-y
                    min-width="auto"
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-text-field
                        v-model="dateTime.time"
                        label="Time taken"
                        prepend-icon="schedule"
                        readonly
                        v-bind="attrs"
                        v-on="on"
                      ></v-text-field>
                    </template>
                    <v-time-picker
                      v-if="dateTime.time"
                      v-model="dateTime.time"
                      color="primary"
                      @click:minute="$refs.timeRef.save(dateTime.time)"
                    ></v-time-picker>
                  </v-menu>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-combobox
                v-model="tmp.tags"
                :items="values.tags"
                label="Tags"
                :search-input.sync="search"
                @change="search = null"
                multiple
                hide-selected
                deletable-chips
                :dense="$vuetify.breakpoint.xsOnly"
                clearable
              >
                <template v-slot:no-data>
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-title>
                        No results matching "
                        <strong>{{ search }}</strong
                        >". Press <kbd>enter</kbd> to create a new one
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </template>
              </v-combobox>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" md="4" sm="6">
              <v-text-field
                label="Camera Model"
                v-model="tmp.model"
                dense
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4" sm="6">
              <v-text-field
                label="Lens"
                v-model="tmp.lens"
                dense
              ></v-text-field>
            </v-col>
            <v-col cols="6" md="4" sm="6">
              <v-text-field
                label="Focal length"
                type="number"
                v-model="tmp.focal_length"
                dense
              ></v-text-field>
            </v-col>
            <v-col cols="6" md="4" sm="6">
              <v-text-field
                label="ISO [ASA]"
                type="number"
                v-model="tmp.iso"
                dense
              ></v-text-field>
            </v-col>
            <v-col cols="6" md="4" sm="6">
              <v-text-field
                label="Aperture"
                type="number"
                step="0.1"
                v-model="tmp.aperture"
                dense
              ></v-text-field>
            </v-col>
            <v-col cols="6" md="4" sm="6">
              <v-text-field
                label="Shutter [s]"
                v-model="tmp.shutter"
                dense
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4" sm="6">
              <v-checkbox
                label="Flash fired?"
                v-model="tmp.flash"
                dense
              ></v-checkbox>
            </v-col>
            <v-col cols="12" md="4" sm="6" class="hidden-sm-and-down">
              <v-text-field
                label="Location [latitude, longitude]"
                v-model="tmp.loc"
                dense
              ></v-text-field>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import common from '../helpers/mixins'

const axios = Vue.axios

export default {
  name: 'Edit',
  mixins: [common],
  props: ['visible', 'current'],
  data: () => ({
    tmp: {},
    menuDate: false,
    menuTime: false,
    search: null,
    submitting: false
  }),
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['values']),
    valid: {
      get () {
        return this.tmp.headline !== '' && !this.submitting
      },
      set (newValue) {
        return newValue
      }
    },
    show: {
      get () {
        return this.visible
      },
      set (value) {
        if (!value) {
          // emit parent List event close
          this.$emit('close')
        }
      }
    },
    linearDim () {
      const dimension = this.tmp.dim || []
      return dimension.join('✕') || ''
    },
    dateTime () {
      const dt = this.tmp.date || this.$date().format('YYYY-MM-DD HH:mm')
      const [date, time] = dt.split(' ')
      return {
        date: date,
        time: time
      }
    }
  },
  watch: {
    visible: function (val) {
      if (val) {
        this.tmp = { ...this.current }
        if (!this.tmp.date) {
          // new image
          this.readExif()
        }
      }
    }
  },
  methods: {
    submit (event) {
      event.preventDefault()
      this.submitting = true
      this.tmp.date = this.dateTime.date + ' ' + this.dateTime.time
      this.tmp.tags = this.tmp.tags ? this.tmp.tags : []
      this.$store.dispatch('app/saveRecord', this.tmp)

      setTimeout(() => {
        this.submitting = false
        this.show = false
      }, 1000)
    },
    readExif () {
      axios.get('exif/' + this.tmp.filename).then((response) => {
        this.tmp = { ...this.tmp, ...response.data }
        // add flash tag if exif flash true
        let tags = this.tmp.tags || []
        if (response.data.flash && tags.indexOf('flash') === -1) {
          tags.push('flash')
          this.tmp = { ...this.tmp, ...{ tags: tags } }
        }
      })
    }
  }
}
</script>

<style scoped>
.v-dialog > .v-card > .v-card__text {
  padding: 0 16px 20px;
}
.row + .row {
  margin-top: 0;
}
</style>
