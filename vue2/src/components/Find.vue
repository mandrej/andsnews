<template>
  <v-card tile light flat class="mt-3">
    <v-card-text>
      <v-form ref="form">
        <v-layout row wrap>
          <v-flex xs12 class="hidden-xs-only">
            <v-text-field
              label="Find text"
              v-model="find.text"
              clearable></v-text-field>
          </v-flex>
          <v-flex xs12>
            <v-select
              label="Find by tags"
              :items="tags"
              v-model="find.tags"
              tags chips clearable autocomplete>
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
          <v-flex xs12>
            <v-select
              label="Find by year"
              :items="years"
              v-model="find.year"
              clearable></v-select>
          </v-flex>
          <v-flex xs12>
            <v-select
              label="Find by month"
              :items="months"
              v-model="find.month"
              clearable></v-select>
          </v-flex>
          <v-flex xs12 class="hidden-xs-only">
            <v-select
              label="Find by camera model"
              :items="models"
              v-model="find.model"
              autocomplete clearable></v-select>
          </v-flex>
          <v-flex xs12>
            <v-select
              label="Find by author"
              :items="authors"
              v-model="find.author"
              autocomplete clearable></v-select>
          </v-flex>
          <v-flex xs12 class="hidden-xs-only">
            <v-select
              label="Find by color"
              :items="colors"
              v-model="find.color"
              autocomplete clearable></v-select>
          </v-flex>
        </v-layout>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import common from '../../helpers/mixins'
import { EventBus } from '../../helpers/event-bus'

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
    ...mapState(['find', 'tags', 'models']),
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
      this.$store.dispatch('saveFindForm', this.find)

      const value = params.join(' AND ')
      if (value) {
        this.$store.dispatch('changeFilter', {
          field: 'search',
          value: value
        })
      } else {
        this.$store.dispatch('changeFilter', {})
      }
      Vue.nextTick(function () {
        EventBus.$emit('reload')
      })
    }
  }
}
</script>
