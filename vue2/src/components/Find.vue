<template>
  <v-card tile light flat>
    <v-card-text>
      <v-layout row wrap>
        <v-flex xs12>
          <v-text-field
            label="by text"
            v-model="tmp.text"
            @keyup.native.enter="submit"
            @change="submit"
            @click:clear="submit"
            clearable></v-text-field>
        </v-flex>
        <v-flex xs12>
          <v-autocomplete
            label="by tags"
            :items="values.tags"
            v-model="tmp.tags"
            chips
            multiple
            hide-selected
            deletable-chips
            @change="submit"
            @click:clear="submit"
            clearable>
          </v-autocomplete>
        </v-flex>
        <v-flex xs12>
          <v-select
            label="by year"
            :items="values.year"
            v-model="tmp.year"
            @change="submit"
            @click:clear="submit"
            clearable></v-select>
        </v-flex>
        <v-flex xs12>
          <v-select
            label="by month"
            :items="months"
            v-model="tmp.month"
            @change="submit"
            @click:clear="submit"
            clearable></v-select>
        </v-flex>
        <v-flex xs12>
          <v-autocomplete
            label="by camera model"
            :items="values.model"
            v-model="tmp.model"
            @change="submit"
            @click:clear="submit"
            clearable></v-autocomplete>
        </v-flex>
        <v-flex xs12>
          <v-autocomplete
            label="by author"
            :items="names"
            v-model="tmp.email"
            @change="submit"
            @click:clear="submit"
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
      return this.values.email.map(email => this.getName(email))
    }
  },
  methods: {
    submit () {
      // remove undefined and empty list
      Object.keys(this.tmp).forEach(key => {
        if (this.tmp[key] == null || this.tmp[key].length === 0) {
          delete this.tmp[key]
        }
      })
      this.$store.dispatch('app/saveFindForm', this.tmp)

      if (Object.keys(this.tmp).length) {
        this.$router.push({ name: 'list', query: this.tmp })
      } else {
        this.$router.push({ name: 'home' })
      }
    }
  }
}
</script>
