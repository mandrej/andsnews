<template>
  <v-dialog v-model="show" hide-overlay lazy max-width="360px">
    <v-card>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn icon flat @click="show = false">
            <v-icon>close</v-icon>
        </v-btn>
      </v-card-actions>
      <v-card-text>
        <p>
          <span class="title">{{item.headline}}</span><br>
          <span class="subheading">
            {{item.date | moment('lll Z')}}<br>
            {{item.author}}
          </span>
        </p>
        <p>
          {{item.aperture ? 'f' + item.aperture : ''}}
          {{item.shutter ? item.shutter + 's' : ''}}
          {{item.iso ? item.iso + ' ASA' : ''}}<br>
          {{item.model}} {{item.lens}}
          {{item.focal_length ? '(' + item.focal_length + 'mm)' : ''}}
        </p>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import Vue from 'vue'
import common from '@/helpers/mixins'

Vue.use(require('vue-moment'))

export default {
  name: 'Info',
  mixins: [ common ],
  props: ['visible', 'item']
}
</script>
