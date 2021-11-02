<template>
  <v-sheet class="pa-4" color="transparent">
    <v-text-field
      class="hidden-md-and-down"
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
      multiple
      hide-selected
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
      item-text="name"
      item-value="value"
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
      v-model.lazy="tmp.lens"
      :items="values.lens"
      label="by lens"
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
  </v-sheet>
</template>

<script>
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'Find',
  data: () => ({
    search: null
  }),
  computed: {
    ...mapState('app', ['busy', 'values', 'find']),
    ...mapGetters('app', ['nickNames']),
    tmp () {
      return { ...this.find }
    },
    months () {
      const locale = this.$date.months()
      return locale.map((month, i) => ({ name: month, value: i + 1 }))
    }
  },
  watch: {
    $route: {
      deep: true,
      immediate: true,
      handler: function (val) {
        let pid = null
        if (val.hash) {
          pid = +val.hash.match(/&pid=(.+)/)[1]
        }
        // adopt to match types in store
        if (Object.prototype.hasOwnProperty.call(val.query, 'year'))
          val.query.year = +val.query.year
        if (Object.prototype.hasOwnProperty.call(val.query, 'month'))
          val.query.month = +val.query.month
        this.$store.dispatch('app/saveFindForm', val.query)
        if (!Object.keys(val.query).length) {
          this.$store.dispatch('app/changeFilter', { reset: false, pid: pid }) // continue
        } else {
          this.$store.dispatch('app/changeFilter', { reset: true, pid: pid }) // new filter
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
      Object.keys(this.tmp).forEach((key) => {
        if (this.tmp[key] == null || this.tmp[key].length === 0) {
          delete this.tmp[key]
        }
      })
      if (Object.keys(this.tmp).length) {
        // https://github.com/vuejs/vue-router/issues/2872
        // eslint-disable-next-line
        this.$router.push({ name: 'list', query: this.tmp }).catch((err) => {})
      } else {
        // eslint-disable-next-line
        this.$router.replace({ name: 'home' }).catch((err) => {})
      }
    }
  }
}
</script>
