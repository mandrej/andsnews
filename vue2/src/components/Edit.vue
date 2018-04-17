<template>
  <v-app light>
    <v-toolbar app>
      <v-icon @click="$router.go(-1)">arrow_back</v-icon>
      <v-toolbar-title>Edit</v-toolbar-title>
    </v-toolbar>

    <v-container grid-list-md mt-5>
      <v-form v-model="valid" ref="form">
        <v-btn @click="submit" :disabled="!valid" color="primary">Submit</v-btn>

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
  </v-app>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Edit',
  data: () => ({
    valid: true,
    requiredRule: [
      v => !!v || 'Required field'
    ],
    rec: {},
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
    this.$store.dispatch('getRecord', this.$route.params.id)
    this.$store.dispatch('getTags')
  },
  computed: {
    ...mapState(['current', 'tags'])
  },
  watch: {
    current (newVal, oldVal) {
      if (!newVal) return
      this.createRecord(newVal)
    }
  },
  methods: {
    createRecord (obj) {
      this.rec = obj
    },
    submit () {
      // console.log(e.target.elements)
      if (this.$refs.form.validate()) {
        this.$store.dispatch('saveRecord', this.rec.safekey)
        this.$router.go(-1)
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

</style>
