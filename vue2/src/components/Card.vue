<template>
  <v-card flat>
    <v-responsive :aspect-ratio="4 / 3">
      <img
        class="lazy"
        :data-src="smallsized + item.filename"
        :title="caption(item)"
        :data-pswp-src="fullsized + item.filename"
        :data-pswp-size="item.dim.join('x')"
        :data-pswp-pid="item.id"
      />
      <p class="text-h6 text-truncate" style="width: 100%">
        {{ item.headline }}
      </p>
    </v-responsive>
    <v-card-text class="d-flex justify-space-between py-2">
      <div style="line-height: 28px">
        {{ item.nick }}, 
        <router-link 
          class="d-inline-block secondary--text text-decoration-none"
          :to="{ name: 'list', query: { year: item.year, month: item.month, day: item.day }}">
          {{ $date(item.date).format('ddd DD.MM.YYYY') }}
        </router-link> {{ $date(item.date).format('HH:mm') }}
      </div>
      <v-btn
        v-if="item.loc"
        icon
        small
        text
        target="blank"
        :href="
          'https://www.google.com/maps/search/?api=1&query=' + [...item.loc]
        "
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
          @click.stop="download"
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
import common from '../helpers/mixins'

export default {
  name: 'Card',
  mixins: [common],
  props: ['item'],
  computed: {
    ...mapState('auth', ['user'])
  },
  methods: {
    download () {
      this.$emit('register-download', {
        headline: this.item.headline,
        email: this.user.email
      })
    },
    removeRecord () {
      this.$emit('remove-record', this.item)
    },
    showEditdForm () {
      this.$emit('edit-record', this.item)
    },
    caption () {
      const { headline, aperture, shutter, iso, model, lens } = this.item
      let tmp = headline
      tmp += shutter ? '\n' + shutter + 's' : ''
      tmp += aperture ? ' f' + aperture : ''
      tmp += iso ? ' ' + iso + ' ASA' : ''
      tmp += model ? '\n' + model : ''
      tmp += lens ? '\n' + lens : ''
      return tmp
    }
  }
}
</script>

<style scoped></style>
