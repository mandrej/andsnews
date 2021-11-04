<template>
  <div
    v-lazy:background-image="getImgSrc(last)"
    class="d-flex flex-column fill-height align-center justify-center lazy last"
  >
    <div class="pa-5" style="position: absolute; top: 0; right: 0">
      <h4 class="text-body-1 white--text text-right">
        ANDрејевићи personal photo album
        <br />
        {{ count }} photos since 2007 and counting
      </h4>
    </div>
    <div class="pa-5" style="position: absolute; bottom: 0; left: 0">
      <p>
        <router-link
          v-for="nick in nickNames"
          :key="nick"
          :title="nick"
          class="d-inline-block pr-4 text-h4 white--text text-decoration-none"
          :to="{ name: 'list', query: { nick: nick } }"
          >{{ nick }}</router-link
        >
      </p>
      <p>
        <router-link
          v-for="year in values.year"
          :key="year"
          :title="year"
          class="d-inline-block pr-3 text-h5 white--text text-decoration-none"
          :to="{ name: 'list', query: { year: year } }"
          >{{ year }}</router-link
        >
      </p>
      <p class="hidden-sm-and-down">
        <router-link
          v-for="tag in values.tags"
          :key="tag"
          :title="tag"
          class="d-inline-block pr-2 text-body-1 white--text text-decoration-none"
          :to="{ name: 'list', query: { tags: tag } }"
          >{{ tag }}</router-link
        >
      </p>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import common from '../helpers/mixins'

export default {
  name: 'Home',
  mixins: [common],
  computed: {
    ...mapState('app', ['last', 'values', 'bucket']),
    ...mapGetters('app', ['nickNames']),
    count () {
      return this.bucket.count
    },
    query () {
      return {
        year: this.last.value,
      }
    },
  },
  mounted () {
    this.$store.dispatch('auth/getPermission')
  },
}
</script>

<style scoped>
.last {
  background-size: cover;
  background-position: center;
}
</style>
