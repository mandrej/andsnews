<template>
  <v-dialog
    v-model="show"
    scrollable
    max-width="800"
    :fullscreen="$vuetify.breakpoint.xsOnly"
    transition="dialog-bottom-transition">
    <v-card tile light>
      <v-app-bar flat light>
        <v-btn @click="submit" color="accent" class="black--text" :disabled="!valid">Submit</v-btn>
        <v-spacer></v-spacer>
        <v-btn icon @click="show = false">
          <v-icon>close</v-icon>
        </v-btn>
      </v-app-bar>
      <v-card-text style="background-color: #f5f5f5">
        <v-container fluid grid-list-lg>
          <v-form v-model="valid" ref="form">
            <v-layout row wrap>
              <v-flex xs12 sm6 md4>
                <v-img
                  cover
                  aspect-ratio="1"
                  :src="getImgSrc(tmp, '400-c')">
                </v-img>
              </v-flex>
              <v-flex xs12 sm6 md8>
                <v-layout row wrap>
                  <v-flex xs12>
                    <v-text-field
                      :label="`Headline for ${tmp.filename}`"
                      v-model="tmp.headline"
                      :rules="requiredRule"
                      required></v-text-field>
                  </v-flex>
                  <v-flex xs12>
                    <v-combobox
                      label="Tags"
                      :items="values.tags"
                      :search-input.sync="search"
                      v-model="tmp.tags"
                      chips
                      multiple
                      hide-selected
                      deletable-chips
                      clearable>
                      <template slot="no-data">
                        <v-list-item>
                          <v-list-item-content>
                            <v-list-item-title>
                              No results matching "<strong>{{ search }}</strong>". Press <kbd>enter</kbd> to create a new one
                            </v-list-item-title>
                          </v-list-item-content>
                        </v-list-item>
                      </template>
                    </v-combobox>
                  </v-flex>
                  <v-flex xs12 sm12 md12>
                    <v-autocomplete
                      label="Author"
                      :items="values.email"
                      v-model="tmp.email"
                      single-line></v-autocomplete>
                  </v-flex>
                  <v-flex xs12 sm12 md12>
                    <v-layout row>
                      <v-flex xs6>
                        <v-menu
                          ref="dateRef"
                          v-model="menuDate"
                          :close-on-content-click="false"
                          :return-value.sync="dateTime.date"
                          transition="scale-transition"
                          offset-y
                          full-width
                          min-width="290px">
                          <template v-slot:activator="{ on }">
                            <v-text-field
                              v-model="dateTime.date"
                              label="Date taken"
                              prepend-icon="event"
                              readonly
                              v-on="on">
                            </v-text-field>
                          </template>
                          <v-date-picker v-model="dateTime.date" no-title scrollable>
                            <v-spacer></v-spacer>
                            <v-btn text color="primary" @click="dateRef = false">Cancel</v-btn>
                            <v-btn text color="primary" @click="$refs.dateRef.save(dateTime.date)">OK</v-btn>
                          </v-date-picker>
                        </v-menu>
                      </v-flex>
                      <v-flex xs6>
                        <v-menu
                          ref="timeRef"
                          v-model="menuTime"
                          :close-on-content-click="false"
                          :nudge-right="40"
                          :return-value.sync="dateTime.time"
                          transition="scale-transition"
                          offset-y
                          full-width
                          max-width="290px"
                          min-width="290px">
                          <template v-slot:activator="{ on }">
                            <v-text-field
                              v-model="dateTime.time"
                              label="time taken"
                              prepend-icon="access_time"
                              readonly
                              v-on="on">
                            </v-text-field>
                          </template>
                          <v-time-picker
                            v-if="dateTime.time"
                            v-model="dateTime.time"
                            full-width
                            @click:minute="$refs.timeRef.save(dateTime.time)">
                          </v-time-picker>
                        </v-menu>
                      </v-flex>
                    </v-layout>
                  </v-flex>
                </v-layout>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Camera Model"
                  v-model="tmp.model"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Lens"
                  v-model="tmp.lens"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Focal length"
                  type="number"
                  v-model="tmp.focal_length"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="ISO [ASA]"
                  type="number"
                  v-model="tmp.iso"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Aperture"
                  type="number"
                  step="0.1"
                  v-model="tmp.aperture"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Shutter [s]"
                  v-model="tmp.shutter"></v-text-field>
              </v-flex>
            </v-layout>
          </v-form>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Edit',
  mixins: [ common ],
  props: ['visible', 'rec'],
  data: () => ({
    valid: true,
    menuDate: false,
    menuTime: false,
    dateTime: {},
    tmp: {},
    search: null
  }),
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['values']),
    show: {
      get () {
        return this.visible
      },
      set (value) {
        if (!value) {
          this.$emit('close')
        }
      }
    }
  },
  watch: {
    rec: function (val) {
      if (JSON.stringify(val) === '{}') return
      const dt = val.date.split('T')
      this.tmp = { ...val }
      this.dateTime = {
        date: dt[0],
        time: dt[1].substring(0, 5)
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
        this.$store.dispatch('app/saveRecord', this.tmp)
        this.show = false
      }
    }
  }
}
</script>
