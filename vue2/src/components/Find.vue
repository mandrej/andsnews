<template>
  <v-card flat light>
    <v-card-title class="hidden-xs-only">Filter</v-card-title>
    <v-card-text>
      <v-text-field
        v-model="tmp.text"
        label="by text"
        @keyup.native.enter="submit"
        @change="submit"
        @click:clear="submit"
        :disabled="disabled"
        clearable
      ></v-text-field>
      <v-autocomplete
        v-model="tmp.tags"
        :items="values.tags"
        label="by tags"
        :search-input.sync="search"
        @change="clearSubmit"
        @click:clear="submit"
        :disabled="disabled"
        chips
        multiple
        hide-selected
        deletable-chips
        autocomplete="off"
        clearable
      ></v-autocomplete>
      <v-select
        v-model="tmp.year"
        :items="values.year"
        label="by year"
        @change="submit"
        @click:clear="submit"
        :disabled="disabled"
        clearable
      ></v-select>
      <v-select
        v-model="tmp.month"
        :items="months"
        label="by month"
        @change="submit"
        @click:clear="submit"
        :disabled="disabled"
        clearable
      ></v-select>
      <v-autocomplete
        v-model="tmp.model"
        :items="values.model"
        label="by camera model"
        @change="submit"
        @click:clear="submit"
        :disabled="disabled"
        clearable
      ></v-autocomplete>
      <v-autocomplete
        v-model="tmp.nick"
        :items="nicks"
        label="by author"
        @change="submit"
        @click:clear="submit"
        :disabled="disabled"
        clearable
      ></v-autocomplete>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Find',
  mixins: [common],
  created () {
    this.$store.dispatch('app/fetchValues')
  },
  data: () => ({
    tmp: {},
    disabled: true,
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
        return this.email2nick(email)
      })
    }
  },
  watch: {
    busy: function (val) {
      this.disabled = val
    },
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
