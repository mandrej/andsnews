<template>
  <v-card flat light>
    <v-card-title class="hidden-xs-only">Filter</v-card-title>
    <v-card-text>
      <v-text-field
        label="by text"
        v-model="tmp.text"
        @keyup.native.enter="submit"
        @change="submit"
        @click:clear="submit"
        clearable></v-text-field>
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
      <v-select
        label="by year"
        :items="values.year"
        v-model="tmp.year"
        @change="submit"
        @click:clear="submit"
        clearable></v-select>
      <v-select
        label="by month"
        :items="months"
        v-model="tmp.month"
        @change="submit"
        @click:clear="submit"
        clearable></v-select>
      <v-autocomplete
        label="by camera model"
        :items="values.model"
        v-model="tmp.model"
        @change="submit"
        @click:clear="submit"
        clearable></v-autocomplete>
      <v-autocomplete
        label="by author"
        :items="nicks"
        v-model="tmp.nick"
        @change="submit"
        @click:clear="submit"
        clearable></v-autocomplete>
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
  data: () => ({
    tmp: {}
  }),
  computed: {
    ...mapState('app', ['find', 'values']),
    months () {
      const arr = [...Array(12 + 1).keys()]
      arr.shift()
      return arr
    },
    nicks () {
      return this.values.email.map(email => {
        return this.email2nick(email)
      })
    }
  },
  watch: {
    find: {
      immediate: true,
      handler: function (val) {
        this.tmp = { ...val }
      }
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
      if (Object.keys(this.tmp).length) {
        // https://github.com/vuejs/vue-router/issues/2872
        // eslint-disable-next-line
        this.$router.push({ name: 'list', query: this.tmp }).catch(err => {})
      } else {
        this.$router.push({ name: 'home' })
      }
    }
  }
}
</script>
