<template>
  <v-card tile light flat>
    <v-card-text>
      <v-btn @click="submit" block flat>
        Search photos
        <v-icon right dark>search</v-icon>
      </v-btn>
      <v-layout row wrap>
        <v-flex xs12 class="hidden-xs-only">
          <v-text-field
            label="by text"
            v-model="tmp.text"
            clearable></v-text-field>
        </v-flex>
        <v-flex xs12>
          <v-autocomplete
            label="by tags"
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
          </v-autocomplete>
        </v-flex>
        <v-flex xs12>
          <v-select
            label="by year"
            :items="values.year"
            v-model="tmp.year"
            clearable></v-select>
        </v-flex>
        <v-flex xs12>
          <v-select
            label="by month"
            :items="months"
            v-model="tmp.month"
            clearable></v-select>
        </v-flex>
        <v-flex xs12>
          <v-autocomplete
            label="by camera model"
            :items="values.model"
            v-model="tmp.model"
            clearable></v-autocomplete>
        </v-flex>
        <v-flex xs12>
          <v-autocomplete
            label="by author"
            :items="names"
            v-model="tmp.author"
            clearable></v-autocomplete>
        </v-flex>
        <v-flex xs12 class="hidden-xs-only">
          <v-autocomplete
            label="by color"
            :items="values.color"
            v-model="tmp.color"
            clearable></v-autocomplete>
        </v-flex>
      </v-layout>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Find',
  mixins: [ common ],
  created () {
    this.$store.dispatch('app/fetchValues')
  },
  computed: {
    ...mapState('app', ['find', 'values']),
    tmp () {
      return { ...this.find }
    },
    months () {
      const arr = [...Array(12 + 1).keys()]
      arr.shift()
      return arr
    },
    names () {
      const arr = [].concat.apply([], this.$authors.map(email => [...email.split('@')[0].split('.')]))
      const set = new Set(arr)
      return [...set]
    }
  },
  methods: {
    submit () {
      let params = []
      const sep = '"' // because of tags:b&w -> tags:"b&w"

      function wrap (key, value) {
        if (key === 'text') {
          params.push(sep + value.toLowerCase() + sep)
        } else {
          params.push(key + ':' + sep + value + sep)
        }
      }

      Object.keys(this.tmp).forEach(key => {
        if (key === 'tags') {
          this.tmp[key].forEach(tag => {
            wrap(key, tag)
          })
        } else {
          if (this.tmp[key]) {
            wrap(key, this.tmp[key])
          }
        }
      })
      // Object.keys(this.tmp).forEach(key => (this.tmp[key] == null || this.tmp[key].length === 0) && delete this.tmp[key])
      // console.log(this.tmp)


      this.$store.dispatch('app/saveFindForm', this.tmp)
      const value = params.join(' AND ')

      if (value) {
        this.$router.push({ name: 'list', params: { 'qs': value } })
      } else {
        this.$router.push({ name: 'home' })
      }
    }
  }
}
</script>
