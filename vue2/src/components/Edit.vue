<template>
  <v-dialog
    v-model="show"
    scrollable
    max-width="800"
    :fullscreen="$vuetify.breakpoint.xsOnly"
    @keydown.esc="show = false"
    transition="dialog-bottom-transition"
  >
    <v-card>
      <v-app-bar>
        <v-btn @click="submit" color="primary" :disabled="!valid">Submit</v-btn>
        <v-spacer></v-spacer>
        <v-btn icon @click="show = false">
          <v-icon>close</v-icon>
        </v-btn>
      </v-app-bar>
      <v-card-text class="pa-2">
        <v-container fluid grid-list-lg>
          <v-form v-model="valid" ref="form">
            <v-layout row wrap>
              <v-flex xs12 sm6 md4>
                <img class="lazy" v-lazy="getImgSrc(tmp, 400)" />
                <v-btn if="user.isAdmin" text block @click="readExif">Read Exif</v-btn>
              </v-flex>
              <v-flex xs12 sm6 md8>
                <v-layout row wrap>
                  <v-flex xs12>
                    <v-text-field
                      v-model="tmp.headline"
                      :rules="requiredRule"
                      :label="`Headline for ${tmp.filename}`"
                      required
                    ></v-text-field>
                  </v-flex>
                  <v-flex xs12>
                    <v-combobox
                      v-model="tmp.tags"
                      :items="values.tags"
                      label="Tags"
                      :search-input.sync="search"
                      @change="search = null"
                      chips
                      multiple
                      hide-selected
                      deletable-chips
                      clearable
                    >
                      <template v-slot:no-data>
                        <v-list-item>
                          <v-list-item-content>
                            <v-list-item-title>
                              No results matching "
                              <strong>{{ search }}</strong>". Press
                              <kbd>enter</kbd> to create a new one
                            </v-list-item-title>
                          </v-list-item-content>
                        </v-list-item>
                      </template>
                    </v-combobox>
                  </v-flex>
                  <v-flex xs12 sm12 md12>
                    <v-autocomplete
                      v-model="tmp.email"
                      :items="values.email"
                      label="Author"
                      single-line
                    ></v-autocomplete>
                  </v-flex>
                  <v-flex xs12 sm12 md12>
                    <v-layout row>
                      <v-flex xs6>
                        <v-menu
                          v-model="menuDate"
                          ref="dateRef"
                          :close-on-content-click="false"
                          :return-value.sync="dateTime.date"
                          transition="scale-transition"
                          offset-y
                          min-width="290px"
                        >
                          <template v-slot:activator="{ on }">
                            <v-text-field
                              v-model="dateTime.date"
                              label="Date taken"
                              prepend-icon="event"
                              readonly
                              v-on="on"
                            ></v-text-field>
                          </template>
                          <v-date-picker v-model="dateTime.date" scrollable>
                            <v-spacer></v-spacer>
                            <v-btn text @click="dateRef = false">Cancel</v-btn>
                            <v-btn text @click="$refs.dateRef.save(dateTime.date)">OK</v-btn>
                          </v-date-picker>
                        </v-menu>
                      </v-flex>
                      <v-flex xs6>
                        <v-menu
                          v-model="menuTime"
                          ref="timeRef"
                          :close-on-content-click="false"
                          :nudge-right="40"
                          :return-value.sync="dateTime.time"
                          transition="scale-transition"
                          offset-y
                          max-width="290px"
                          min-width="290px"
                        >
                          <template v-slot:activator="{ on }">
                            <v-text-field
                              v-model="dateTime.time"
                              label="time taken"
                              prepend-icon="access_time"
                              readonly
                              v-on="on"
                            ></v-text-field>
                          </template>
                          <v-time-picker
                            v-if="dateTime.time"
                            v-model="dateTime.time"
                            @click:minute="$refs.timeRef.save(dateTime.time)"
                          ></v-time-picker>
                        </v-menu>
                      </v-flex>
                    </v-layout>
                  </v-flex>
                </v-layout>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field label="Camera Model" v-model="tmp.model"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field label="Lens" v-model="tmp.lens"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field label="Focal length" type="number" v-model="tmp.focal_length"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field label="ISO [ASA]" type="number" v-model="tmp.iso"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field label="Aperture" type="number" step="0.1" v-model="tmp.aperture"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field label="Shutter [s]" v-model="tmp.shutter"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field color="error" readonly label="File size [bytes]" v-model="tmp.size"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  color="error"
                  readonly
                  label="Dimension [width, height]"
                  v-model="tmp.dim"
                ></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field label="Location [latitude, longitude]" v-model="tmp.loc"></v-text-field>
              </v-flex>
            </v-layout>
          </v-form>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

const axios = Vue.axios

export default {
  name: 'Edit',
  mixins: [common],
  props: ['visible', 'rec'],
  data: () => ({
    menuDate: false,
    menuTime: false,
    tmp: {},
    search: null
  }),
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['values']),
    valid: {
      get () {
        return Boolean(this.tmp.date)
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
          this.$emit('close')
        }
      }
    },
    dateTime () {
      return this.splitDate(this.tmp.date)
    }
  },
  watch: {
    rec: function (val) {
      this.tmp = { ...val }
      if (!val.date) {
        this.readExif()
        return
      }
    }
  },
  methods: {
    submit () {
      if (this.$refs.form.validate()) {
        if (this.dateTime.time.length === 5) {
          this.dateTime.time += ':00'
        }
        this.tmp.date = this.dateTime.date + 'T' + this.dateTime.time
        this.tmp.tags = (this.tmp.tags) ? this.tmp.tags : []

        this.$store.dispatch('app/saveRecord', this.tmp)
        this.show = false
      }
    },
    readExif () {
      axios.get('exif/' + this.tmp.filename).then(response => {
        const val = response.data
        this.tmp = { ...this.tmp, ...val }
      })
    }
  }
}
</script>
