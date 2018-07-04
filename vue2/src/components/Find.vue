<template>
  <v-card tile light flat>
    <v-card-text>
      <v-form ref="form">
        <p class="subheadings">Search images</p>
        <v-layout row wrap>
          <v-flex xs12 class="hidden-xs-only">
            <v-text-field
              label="by text"
              v-model="data.text"
              clearable></v-text-field>
          </v-flex>
          <v-flex xs12>
            <v-autocomplete
              label="by tags"
              :items="tags"
              v-model="data.tags"
              multiple chips clearable>
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
          <v-flex xs12>
            <v-select
              label="by year"
              :items="years"
              v-model="data.year"
              clearable></v-select>
          </v-flex>
          <v-flex xs12>
            <v-select
              label="by month"
              :items="months"
              v-model="data.month"
              clearable></v-select>
          </v-flex>
          <v-flex xs12 class="hidden-xs-only">
            <v-autocomplete
              label="by camera model"
              :items="models"
              v-model="data.model"
              clearable></v-autocomplete>
          </v-flex>
          <v-flex xs12>
            <v-autocomplete
              label="by author"
              :items="authors"
              v-model="data.author"
              clearable></v-autocomplete>
          </v-flex>
          <v-flex xs12 class="hidden-xs-only">
            <v-autocomplete
              label="by color"
              :items="colors"
              v-model="data.color"
              clearable></v-autocomplete>
          </v-flex>
        </v-layout>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'
import { EventBus } from '@/helpers/event-bus'

export default {
  name: 'Find',
  mixins: [ common ],
  props: ['visible'],
  data: () => ({
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
    ...mapState('All', ['find', 'tags', 'models']),
    data () {
      return Object.assign({}, this.find)
    },
    years () {
      const start = 2007
      const end = (new Date()).getFullYear()
      return [...Array(end - start + 1).keys()].map(n => start + n).reverse()
    },
    months () {
      const tmp = [...Array(12 + 1).keys()]
      tmp.shift()
      return tmp
    }
  },
  mounted () {
    EventBus.$on('submit', this.submit)
  },
  methods: {
    submit () {
      let params = []

      if (this.data.tags) {
        this.data.tags.forEach(tag => {
          params.push('tags:' + tag)
        })
      }
      if (this.data.text) {
        params.push(this.data.text)
      }
      if (this.data.year) {
        params.push('year:' + this.data.year)
      }
      if (this.data.month) {
        params.push('month:' + this.data.month)
      }
      if (this.data.model) {
        params.push('model:' + this.data.model)
      }
      if (this.data.author) {
        params.push('author:' + this.data.author)
      }
      if (this.data.color) {
        params.push('color:' + this.data.color)
      }
      this.$store.dispatch('All/saveFindForm', this.data)

      const value = params.join(' AND ')
      if (value) {
        this.$store.dispatch('All/changeFilter', {
          field: 'search',
          value: value
        })
      } else {
        this.$store.dispatch('All/changeFilter', {})
      }
    }
  }
}
</script>
