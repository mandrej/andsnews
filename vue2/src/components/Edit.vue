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
        <v-btn @click="submit" :disabled="!valid">Submit</v-btn>
      </v-toolbar>
      <v-card-text>
        <img v-lazy="getImgSrc(current, 's')">
        <v-container grid-list-md mt-3>
          <v-form v-model="valid" ref="form">
            <v-layout row wrap>
              <v-flex xs12>
                <v-text-field
                  :label="`Headline for ${current.filename}`"
                  v-model="current.headline"
                  :rules="requiredRule"
                  required></v-text-field>
              </v-flex>
              <v-flex xs12>
                <v-select
                  label="Tags"
                  :items="tags"
                  v-model="current.tags"
                  chips
                  tags
                  clearable
                  autocomplete>
                  <template slot="selection" slot-scope="data">
                    <v-chip
                      close
                      @input="data.parent.selectItem(data.item)"
                      :selected="data.selected">
                      <strong>{{ data.item }}</strong>&nbsp;
                    </v-chip>
                  </template>
                </v-select>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-select
                  label="Author"
                  :items="authors"
                  v-model="current.author"
                  autocomplete
                  single-line></v-select>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Date taken"
                  v-model="current.date"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Camera Model"
                  v-model="current.model"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Lens"
                  v-model="current.lens"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Focal length"
                  type="number"
                  v-model="current.focal_length"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="ISO [ASA]"
                  type="number"
                  v-model="current.iso"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Aperture"
                  type="number"
                  step="0.1"
                  v-model="current.aperture"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Shutter [s]"
                  v-model="current.shutter"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Color"
                  v-model="current.color"
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
import common from '../../helpers/mixins'
import { EventBus } from '../../helpers/event-bus'

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
    ]
  }),
  computed: {
    ...mapState(['current', 'tags'])
  },
  methods: {
    submit () {
      if (this.$refs.form.validate()) {
        this.$store.dispatch('saveRecord', this.current)
        EventBus.$emit('goto')
        this.show = false
      }
    }
  }
}
</script>
