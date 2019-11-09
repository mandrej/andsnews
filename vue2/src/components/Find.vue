<template>
  <v-card flat light>
    <v-card-title class="hidden-xs-only">Filter</v-card-title>
    <v-card-text>
      <v-text-field
        v-model.lazy="tmp.text"
        label="by text"
        @change="submit"
        @keyup.native.enter="submit"
        :disabled="busy"
        clearable
      ></v-text-field>
      <v-autocomplete
        v-model.lazy="tmp.tags"
        :items="values.tags"
        label="by tags"
        :search-input.sync="search"
        @change="clearSubmit"
        :disabled="busy"
        chips
        multiple
        hide-selected
        deletable-chips
        autocomplete="off"
        clearable
      ></v-autocomplete>
      <v-select
        v-model.lazy="tmp.year"
        :items="values.year"
        label="by year"
        @change="submit"
        :disabled="busy"
        clearable
      ></v-select>
      <v-select
        v-model.lazy="tmp.month"
        :items="months"
        label="by month"
        @change="submit"
        :disabled="busy"
        clearable
      ></v-select>
      <v-autocomplete
        v-model.lazy="tmp.model"
        :items="values.model"
        label="by camera model"
        @change="submit"
        :disabled="busy"
        clearable
      ></v-autocomplete>
      <v-autocomplete
        v-model.lazy="tmp.nick"
        :items="nicks"
        label="by author"
        @change="submit"
        :disabled="busy"
        clearable
      ></v-autocomplete>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Find',

  created () {
    this.$store.dispatch('app/fetchValues')
  },
  data: () => ({
    tmp: {},
    search: null
  }),
  computed: {
    ...mapState('app', ['busy', 'find', 'values']),
    months () {
      const arr = [...Array(12 + 1).keys()]
      arr.shift()
      return arr
    },
    nicks () {
      return this.values.email.map(email => {
        return email.match(/[^@]+/)[0].split('.')[0]
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
    clearSubmit () {
      this.search = null
      this.submit()
    },
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
        this.$router.push({ name: 'list', query: this.tmp }).catch(err => { })
      } else {
        this.$router.push({ name: 'home' })
      }
    }
  }
}
</script>
