<template>
  <v-dialog
    v-model="show"
    lazy fullscreen hide-overlay scrollable
    transition="dialog-bottom-transition">
    <v-card tile>
      <v-toolbar dark color="primary">
        <v-btn icon @click="show = false">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title class="headline">Edit</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn @click="submit" color="secondary" :disabled="!valid">Submit</v-btn>
      </v-toolbar>
      <v-card-text>
        <v-container grid-list-md mt-3>
          <v-form v-model="valid" ref="form">
            <v-layout row wrap>
              <v-flex xs12 sm6 md4>
                <img v-lazy="getImgSrc(data, 's')">
              </v-flex>
              <v-flex xs12 sm6 md8>
                <v-layout row wrap>
                  <v-flex xs12 d-flex>
                    <v-text-field
                      :label="`Headline for ${data.filename}`"
                      v-model="data.headline"
                      :rules="requiredRule"
                      required></v-text-field>
                  </v-flex>
                  <v-flex xs12 d-flex>
                    <v-autocomplete
                      label="Tags"
                      :items="tags"
                      v-model="data.tags"
                      chips
                      tags
                      clearable>
                      <template slot="selection" slot-scope="data">
                        <v-chip
                          close
                          @input="data.parent.selectItem(data.item)"
                          :selected="data.selected">
                          <strong>{{ data.item }}</strong>&nbsp;
                        </v-chip>
                      </template>
                    </v-autocomplete>
                  </v-flex>
                  <v-flex xs12 sm12 md12 d-flex>
                    <v-autocomplete
                      label="Author"
                      :items="authors"
                      v-model="data.author"
                      single-line></v-autocomplete>
                  </v-flex>
                  <v-flex xs12 sm12 md12 d-flex>
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
                  v-model="data.model"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Lens"
                  v-model="data.lens"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Focal length"
                  type="number"
                  v-model="data.focal_length"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="ISO [ASA]"
                  type="number"
                  v-model="data.iso"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Aperture"
                  type="number"
                  step="0.1"
                  v-model="data.aperture"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Shutter [s]"
                  v-model="data.shutter"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Color"
                  v-model="data.color"
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
import Vue from 'vue'
import { mapState } from 'vuex'
import common from '@/helpers/mixins'
import { EventBus } from '@/helpers/event-bus'

export default {
  name: 'Edit',
  mixins: [ common ],
  props: ['visible'],
  data: () => ({
    valid: true,
    requiredRule: [
      value => !!value || 'Required.'
    ],
    authors: [
      'milan.andrejevic@gmail.com',
      'mihailo.genije@gmail.com',
      'svetlana.andrejevic@gmail.com',
      'ana.devic@gmail.com',
      'dannytaboo@gmail.com',
      'zile.zikson@gmail.com'
    ],
    dateTime: {},
    menuDate: false,
    menuTime: false
  }),
  computed: {
    ...mapState('All', ['current', 'tags']),
    data () {
      return Object.assign({}, this.current)
    },
  },
  watch: {
    'data.date' (val) {
      if (!val) return
      const tmp = val.split('T')
      // this.dateTime = Object.assign({}, this.dateTime, {
      //   date: tmp[0],
      //   time: tmp[1]
      // })
      Vue.set(this.dateTime, 'date', tmp[0])
      Vue.set(this.dateTime, 'time', tmp[1])
    }
  },
  methods: {
    submit () {
      if (this.$refs.form.validate()) {
        if (this.dateTime.time.length === 5) {
          this.dateTime.time += ':00'
        }
        this.data.date = this.dateTime.date + 'T' + this.dateTime.time
        this.$store.dispatch('All/saveRecord', this.data)
        EventBus.$emit('goto')
        this.show = false
      }
    }
  }
}
</script>

<style scoped>
.flex img {
  max-width: 100%;
}
</style>
