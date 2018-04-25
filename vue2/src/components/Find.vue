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
        <v-toolbar-title>Find</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn @click="reset" color="secondary">Reset</v-btn>
        <v-btn @click="submit" :disabled="!valid" light>Find</v-btn>
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
                  :items="tags"
                  v-model="find.tags"
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
                <v-text-field
                  label="Find by year"
                  v-model="find.year"
                  type="number"
                  :min="2007"
                  :max="(new Date()).getFullYear()"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field
                  label="Find by month"
                  v-model="find.month"
                  type="number"
                  :min="1"
                  :max="12"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-select
                  label="Find by camera model"
                  :items="models"
                  v-model="find.model"
                  autocomplete
                  clearable
                  single-line></v-select>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-select
                  label="Find by author"
                  :items="authors"
                  v-model="find.author"
                  autocomplete
                  clearable
                  single-line></v-select>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-select
                  label="Find by color"
                  :items="colors"
                  v-model="find.color"
                  autocomplete
                  clearable
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
import common from '../../helpers/mixins'
import { EventBus } from '../../helpers/event-bus'

export default {
  name: 'Find',
  mixins: [ common ],
  props: ['visible'],
  data: () => ({
    valid: true,
    authors: ['milan', 'mihailo', 'genije', 'svetlana', 'andrejevic', 'ana', 'devic', 'dannytaboo', 'zile', 'zikson'],
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
  computed: {
    ...mapState(['find', 'tags', 'models'])
  },
  methods: {
    reset () {
      this.$store.dispatch('changeFind', this.blank)
    },
    submit () {
      let params = []
      if (this.$refs.form.validate()) {
        if (this.find.tags) {
          this.find.tags.forEach(tag => {
            params.push('tags:' + tag)
          })
        }
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
        this.$store.dispatch('changeFind', this.find)

        const value = params.join(' AND ')
        if (value) {
          this.$store.dispatch('changeFilter', {
            field: 'search',
            value: value
          })
          this.show = false
          EventBus.$emit('reload')
          // this.$router.push({name: 'search', params: {term: value}})
        } else {
          this.$store.dispatch('changeFilter', {})
          this.show = false
        }
      }
    }
  }
}
</script>
