<template>
  <v-dialog
    v-model="show"
    lazy
    fullscreen
    transition="dialog-bottom-transition"
    :overlay="false"
    scrollable>
    <v-card tile>
      <v-toolbar card dark color="primary">
        <v-btn icon @click.native="show = false">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>Edit</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn @click="submit" :disabled="!valid" light>Submit</v-btn>
      </v-toolbar>
      <v-card-text>
        <v-container grid-list-md mt-3>
          <v-form v-model="valid" ref="form">
            <v-layout row wrap>
              <v-flex xs12>
                <v-text-field
                  :label="`Headline for ${rec.filename}`"
                  v-model="rec.headline"
                  :rules="requiredRule"
                  required></v-text-field>
              </v-flex>
              <v-flex xs12>
                <v-select
                  label="Tags"
                  v-model="rec.tags"
                  chips
                  tags
                  :items="tags"
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
                  :items="authors"
                  v-model="rec.author"
                  label="Author"
                  autocomplete
                  single-line></v-select>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Date taken"
                  v-model="rec.date"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Camera Model"
                  v-model="rec.model"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Lens"
                  v-model="rec.lens"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Focal length"
                  type="number"
                  v-model="rec.focal_length"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="ISO [ASA]"
                  type="number"
                  v-model="rec.iso"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Aperture"
                  type="number"
                  step="0.1"
                  v-model="rec.aperture"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Shutter [s]"
                  v-model="rec.shutter"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Color"
                  v-model="rec.color"
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

export default {
  name: 'Edit',
  mixins: [ common ],
  props: ['visible', 'rec'],
  data: () => ({
    valid: true,
    requiredRule: [
      v => !!v || 'Required field'
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
  created () {
    this.$store.dispatch('getTags')
  },
  computed: {
    ...mapState(['tags'])
  },
  methods: {
    submit () {
      if (this.$refs.form.validate()) {
        this.$store.dispatch('saveRecord', this.rec)
        this.show = false
      }
    }
  }
}
</script>
