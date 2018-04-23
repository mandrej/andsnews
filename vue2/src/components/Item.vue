<template>
  <div>
    <v-dialog v-model="info" hide-overlay lazy max-width="360px">
      <v-card>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn icon flat @click.stop="info = false">
             <v-icon>close</v-icon>
          </v-btn>
        </v-card-actions>
        <v-card-text>
          <p class="title">{{dateFormat(rec.date)}}</p>
          <p>
            {{rec.author}}<br>
            {{rec.model}} {{rec.lens}} ({{rec.focal_length}}mm)
          </p>
          <p class="title">f{{rec.aperture}} {{rec.shutter}}s {{rec.iso}} ASA</p>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog
      v-model="show"
      lazy
      fullscreen
      transition="scale-transition"
      hide-overlay
      scrollable>
      <v-card tile>
        <v-toolbar card dark color="primary">
          <v-btn icon @click.native="show = false">
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title>{{rec.headline || title}}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon class="white--text" :href="`/api/download/${rec.safekey}`" flat>
            <v-icon>file_download</v-icon>
          </v-btn>
          <v-btn icon class="white--text" @click="info = true" flat>
            <v-icon>more_vert</v-icon>
          </v-btn>
        </v-toolbar>
        <v-card-media :src="getImgSrc(rec)" height="100%" contain></v-card-media>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import common from '../../helpers/mixins'

export default {
  name: 'Item',
  mixins: [ common ],
  props: ['visible', 'rec'],
  data: () => ({
    title: 'Not found',
    info: false
  })
}
</script>
