<template>
  <v-card flat>
    <v-responsive :aspect-ratio="4/3">
      <img
        class="lazy"
        :data-src="getImgSrc(item, 400)"
        :title="caption()"
        :data-pswp-size="item.dim.join('x')"
        :data-pswp-src="getImgSrc(item)"
        :data-pswp-pid="item.id"
      />
      <p class="text-h6">{{item.headline}}</p>
    </v-responsive>
    <v-card-text class="d-flex justify-space-between py-2">
      <div
        style="line-height: 28px"
      >{{item.nick}}, {{$date(item.date).format('ddd DD.MM.YYYY HH:mm')}}</div>
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
        <v-btn v-if="user.isAdmin" icon small text @click.stop="removeRecord">
          <v-icon>delete</v-icon>
        </v-btn>
        <v-btn icon small text @click.stop="showEditdForm">
          <v-icon>edit</v-icon>
        </v-btn>
        <v-btn
          icon
          small
          text
          @click="register"
          :href="`/api/download/${item.filename}`"
          :download="item.filename"
        >
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
  props: ['item'],
  mixins: [common],
  computed: {
    ...mapState('auth', ['user'])
  },
  methods: {
    showEditdForm () {
      this.$store.dispatch('app/setCurrent', this.item)
      this.$eventBus.emit('show-edit')
    },
    removeRecord () {
      this.$store.dispatch('app/setCurrent', this.item)
      this.$eventBus.emit('show-confirm')
    },
    register () {
      // eslint-disable-next-line no-undef
      gtag('event', 'download', {
        event_category: 'engagement',
        event_label: this.item.headline + ' (' + this.user.email + ')',
        value: 1
      })
    },
    caption () {
      const { headline, aperture, shutter, iso } = this.item
      let tmp = headline
      tmp += (aperture) ? ' f' + aperture : ''
      tmp += (shutter) ? ', ' + shutter + 's' : ''
      tmp += (iso) ? ', ' + iso + ' ASA' : ''
      return tmp
    }
  }
}
</script>
