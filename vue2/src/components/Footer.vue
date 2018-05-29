<template>
  <v-footer height="auto" app>
    <v-layout row px-3>
      <v-flex xs4 py-3>
        <span class="hidden-xs-only">ANDS &copy; 2007-</span>{{version}}
      </v-flex>
      <v-flex xs4 text-xs-center v-if="top">
        <v-btn fab small flat @click="$vuetify.goTo(0)">
          <v-icon>arrow_upward</v-icon>
        </v-btn>
      </v-flex>
    </v-layout>
  </v-footer>
</template>

<script>

export default {
  name: 'Footer',
  props: ['version', 'top']
}
</script>
