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
          <span class="title">{{current.headline}}</span><br>
          <span class="subheading">{{dateFormat(current)}}</span><br>
          <span class="subheading">
            {{current.aperture ? 'f' + current.aperture : ''}}
            {{current.shutter ? current.shutter + 's' : ''}}
            {{current.iso ? current.iso + ' ASA' : ''}}
          </span>
        </p>
        <p>
          {{current.author}}<br>
          {{current.model}} {{current.lens}}
          {{current.focal_length ? '(' + current.focal_length + 'mm)' : ''}}
        </p>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Info',
  mixins: [ common ],
  props: ['visible'],
  computed: {
    ...mapState('All', ['current'])
  }
}
</script>
