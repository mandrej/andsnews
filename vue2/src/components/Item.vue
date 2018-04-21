<template>
  <v-dialog
    v-model="show"
    lazy
    fullscreen
    transition="scale-transition"
    :overlay="false"
    scrollable>
    <v-card tile>
      <v-toolbar card dark color="primary">
        <v-btn icon @click.native="show = false">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>{{rec.headline || title}}</v-toolbar-title>
        <v-spacer></v-spacer>
        <!-- <v-btn @click="submit" :disabled="!valid" light>Submit</v-btn> -->
      </v-toolbar>
      <v-card-media :src="getImgSrc(rec)" height="100%" contain></v-card-media>
    </v-card>
  </v-dialog>
</template>

<script>
import common from '../../helpers/mixins'

export default {
  name: 'Item',
  mixins: [ common ],
  props: ['visible', 'rec'],
  data: () => ({
    title: 'Not found'
  })
}
</script>
