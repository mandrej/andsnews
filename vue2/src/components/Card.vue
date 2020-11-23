<template>
  <v-card flat>
    <v-responsive :aspect-ratio="4/3">
      <img
        class="lazy"
        :data-src="getImgSrc(item, 400)"
        :title="caption(item)"
        :data-pswp-size="item.dim.join('x')"
        :data-pswp-src="getImgSrc(item)"
        :data-pswp-pid="item.id"
      />
      <p class="title">{{item.headline}}</p>
    </v-responsive>
    <v-card-text class="d-flex justify-space-between py-2">
      <div
        style="line-height: 28px"
      >by {{item.nick}} at {{$date(item.date).format('ddd, MMM DD, YY HH:mm')}}</div>
      <v-btn
        v-if="item.loc"
        icon
        small
        text
        target="blank"
        :href="'https://www.google.com/maps/search/?api=1&query=' + [...item.loc]"
      >
        <v-icon>my_location</v-icon>
      </v-btn>
    </v-card-text>
    <template v-if="user.isAuthorized">
      <v-divider></v-divider>
      <v-card-actions class="justify-space-between">
        <v-btn v-if="user.isAdmin" icon small text @click.stop="removeRecord(item)">
          <v-icon>delete</v-icon>
        </v-btn>
        <v-btn icon small text @click.stop="showEditdForm(item)">
          <v-icon>edit</v-icon>
        </v-btn>
        <v-btn icon small text :href="`/api/download/${item.filename}`" :download="item.filename">
          <v-icon>file_download</v-icon>
        </v-btn>
      </v-card-actions>
    </template>
  </v-card>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Card',
  components: {
  },
  props: ['item'],
  mixins: [common],
  computed: {
    ...mapState('auth', ['user'])
  },
  methods: {
    showEditdForm (rec) {
      this.$store.dispatch('app/setCurrent', rec)
      this.$eventBus.emit('show-edit')
    },
    removeRecord (rec) {
      this.$store.dispatch('app/setCurrent', rec)
      this.$eventBus.emit('show-confirm')
    },
    caption (rec) {
      let tmp = rec.headline
      tmp += (rec.aperture) ? ' f' + rec.aperture : ''
      tmp += (rec.shutter) ? ', ' + rec.shutter + 's' : ''
      tmp += (rec.iso) ? ', ' + rec.iso + ' ASA' : ''
      return tmp
    }
  }
}
</script>
