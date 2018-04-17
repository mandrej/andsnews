<template>
  <v-dialog
    v-model="show"
    fullscreen
    transition="dialog-bottom-transition"
    :overlay="false"
    scrollable>
    <v-card tile>
      <v-toolbar card dark color="primary">
        <v-btn icon @click.native="show=false">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>Find</v-toolbar-title>
        <v-spacer></v-spacer>
        <!-- <v-toolbar-items> -->
          <v-btn @click="reset" color="secondary">Reset</v-btn>
          <v-btn @click="submit" :disabled="!valid" light>Find</v-btn>
        <!-- </v-toolbar-items> -->
      </v-toolbar>
      <v-card-text>
        <v-container grid-list-md mt-3>
          <v-form v-model="valid" ref="form">
            <v-layout row wrap>
              <v-flex xs12 class="hidden-xs-only">
                <v-text-field
                  label="Find text"
                  v-model="find.text"></v-text-field>
              </v-flex>
              <v-flex xs12>
                <v-select
                  label="Find by tags"
                  v-model="find.tags"
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
                <v-text-field
                  label="Find by year"
                  v-model="find.year"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Find by month"
                  v-model="find.month"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-select
                  :items="models"
                  v-model="find.model"
                  label="Find by camera model"
                  autocomplete
                  single-line></v-select>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-select
                  :items="authors"
                  v-model="find.author"
                  label="Find by author"
                  autocomplete
                  single-line></v-select>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-select
                  :items="colors"
                  v-model="find.color"
                  label="Find by color"
                  autocomplete
                  single-line></v-select>
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

export default {
  name: 'Find',
  props: ['visible'],
  data: () => ({
    valid: true,
    authors: [
      'milan.andrejevic@gmail.com',
      'mihailo.genije@gmail.com',
      'svetlana.andrejevic@gmail.com',
      'ana.devic@gmail.com',
      'dannytaboo@gmail.com',
      'zile.zikson@gmail.com'
    ],
    colors: ['red', 'orange', 'yellow', 'green', 'blue', 'violet', 'dark', 'medium', 'light'],
    blank: {
      tags: [],
      text: '',
      year: '',
      month: '',
      model: '',
      author: '',
      color: ''
    }
  }),
  created () {
    this.$store.dispatch('getTags')
    this.$store.dispatch('getModels')
  },
  computed: {
    ...mapState(['find', 'filter', 'tags', 'models']),
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
  methods: {
    reset () {
      // this.find = {...this.blank}
      this.$store.dispatch('changeFind', this.blank)
      // this.$store.dispatch('changeFilter', {})
    },
    submit () {
      let params = []
      if (this.$refs.form.validate()) {
        this.find.tags.forEach(tag => {
          params.push('tags:' + tag)
        })
        if (this.find.text) {
          params.push(this.find.text)
        }
        if (this.find.year) {
          params.push('year:' + this.find.year)
        }
        if (this.find.month) {
          params.push('month:' + this.find.month)
        }
        if (this.find.model) {
          params.push('model:' + this.find.model)
        }
        if (this.find.author) {
          params.push('author:' + this.find.author)
        }
        if (this.find.color) {
          params.push('color:' + this.find.color)
        }

        const value = params.join(' AND ')
        if (value) {
          this.$store.dispatch('changeFind', this.find)
          this.$store.dispatch('changeFilter', {
            field: 'search',
            value: value
          })
          this.$router.push({name: 'search', params: {term: value}})
        }
      }
    }
  }
}
</script>
