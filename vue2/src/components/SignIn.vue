<template>
  <transition name="fade" mode="out-in">
    <v-avatar size="36px" @click="signHandler" style="cursor: pointer">
      <v-img v-if="photoUrl" :src="photoUrl"></v-img>
      <v-img v-else src="/static/img/Google__G__Logo.svg"></v-img>
    </v-avatar>
  </transition>
</template>

<script>
import { mapState } from 'vuex'
import { EventBus } from '@/helpers/event-bus'

export default {
  name: 'SignIn',
  data: () => ({
    photoUrl: null
  }),
  computed: {
    ...mapState('auth', ['user'])
  },
  mounted () {
    this.photoUrl = this.user && this.user.photo
    EventBus.$on('signin', user => {
      this.photoUrl = user && user.photo // url or undefined
    })
  },
  methods: {
    signHandler () {
      this.$store.dispatch('auth/signIn')
    }
  }
}
</script>
