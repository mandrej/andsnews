<template>
  <v-footer height="auto" app>
    <v-layout row px-3>
      <v-flex xs4 py-3>
        <span class="hidden-xs-only">ANDS &copy; 2007-</span>{{version}}
      </v-flex>
      <v-flex xs4 text-xs-center>
        <slot name="gotop"/>
      </v-flex>
    </v-layout>
  </v-footer>
</template>

<script>
export default {
  name: 'Footer',
  computed: {
    version () {
      return process.env.VUE_APP_VERSION.match(/.{1,4}/g).join('.')
    }
  }
}
</script>
