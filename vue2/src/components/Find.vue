<template>
  <v-card flat>
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
        :items="nickNames"
        label="by author"
        @change="submit"
        :disabled="busy"
        clearable
      ></v-autocomplete>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'Find',
  data: () => ({
    tmp: {},
    search: null
  }),
  computed: {
    ...mapState('app', ['busy', 'find', 'values']),
    ...mapGetters('app', ['nickNames']),
    months () {
      const arr = [...Array(12 + 1).keys()]
      arr.shift()
      return arr
    }
  },
  watch: {
    find: {
      immediate: true,
      handler: function (val) {
        this.tmp = { ...val }
      }
    },
    '$route.query': {
      immediate: true,
      handler: function (val) {
        const tmp = {}
        Object.keys(val).forEach(key => {
          if (!isNaN(val[key])) {
            tmp[key] = Number(val[key])
          } else if (Array.isArray(val[key])) {
            tmp[key] = [...val[key]]
          } else {
            tmp[key] = val[key]
          }
        })
        this.$store.dispatch('app/saveFindForm', tmp)

        if (Object.keys(tmp).length) {
          this.$store.dispatch('app/changeFilter', { reset: true })
        } else {
          // eslint-disable-next-line
          this.$router.replace({ name: 'home' }).catch(err => { })
        }
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
        // eslint-disable-next-line
        this.$router.replace({ name: 'home' }).catch(err => { })
      }
    }
  }
}
</script>
