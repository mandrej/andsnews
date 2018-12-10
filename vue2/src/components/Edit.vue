<template>
  <v-dialog
    v-model="show"
    lazy fullscreen hide-overlay scrollable
    transition="dialog-bottom-transition">
    <v-card tile light>
      <v-toolbar light class="aperture">
        <v-btn icon @click="show = false">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title class="headline">Edit</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn @click="submit" color="accent" class="black--text" :disabled="!valid">Submit</v-btn>
      </v-toolbar>
      <v-card-text>
        <v-container grid-list-lg>
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
                      v-model="tmp.tags"
                      chips
                      multiple
                      clearable>
                      <template slot="selection" slot-scope="data">
                        <v-chip
                          close
                          :selected="data.selected"
                          @input="data.parent.selectItem(data.item)">
                          <strong>{{ data.item }}</strong>&nbsp;
                        </v-chip>
                      </template>
                    </v-combobox>
                  </v-flex>
                  <v-flex xs12 sm12 md12>
                    <v-autocomplete
                      label="Author"
                      :items="$authors"
                      v-model="tmp.author"
                      single-line></v-autocomplete>
                  </v-flex>
                  <v-flex xs12 sm12 md12>
                    <v-layout row>
                      <v-flex xs6>
                        <v-menu
                          ref="dateRef"
                          :close-on-content-click="false"
                          v-model="menuDate"
                          :nudge-right="40"
                          :return-value.sync="dateTime.date"
                          lazy
                          full-width
                          transition="scale-transition"
                          max-width="290px"
                          offset-y>
                          <v-text-field
                            slot="activator"
                            v-model="dateTime.date"
                            label="Date taken"
                            readonly></v-text-field>
                          <v-date-picker v-model="dateTime.date" @change="$refs.dateRef.save(dateTime.date)"></v-date-picker>
                        </v-menu>
                      </v-flex>
                      <v-flex xs6>
                        <v-menu
                          ref="timeRef"
                          :close-on-content-click="false"
                          v-model="menuTime"
                          :nudge-right="40"
                          :return-value.sync="dateTime.time"
                          lazy
                          full-width
                          transition="scale-transition"
                          max-width="290px"
                          offset-y>
                          <v-text-field
                            slot="activator"
                            v-model="dateTime.time"
                            label="time taken"
                            readonly></v-text-field>
                          <v-time-picker v-model="dateTime.time" format="24hr" @change="$refs.timeRef.save(dateTime.time)"></v-time-picker>
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
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Color"
                  v-model="tmp.color"
                  disabled></v-text-field>
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
    requiredRule: [
      value => !!value || 'Required.'
    ],
    menuDate: false,
    menuTime: false,
    dateTime: {},
    tmp: {}
  }),
  computed: {
    ...mapState('app', ['values'])
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
