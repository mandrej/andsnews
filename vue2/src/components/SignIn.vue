<template>
  <v-fade-transition mode="out-in" hide-on-leave>
    <v-avatar size="40px" @click="signHandler" style="cursor: pointer">
      <img v-if="photoUrl" :src="photoUrl" />
      <img v-else src="/static/img/Google__G__Logo.svg" />
    </v-avatar>
  </v-fade-transition>
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
      if (this.user && this.user.uid) {
        this.$gtag.event('login', {
          value: this.user.uid
        })
      }
    })
  },
  methods: {
    signHandler () {
      this.$store.dispatch('auth/signIn')
    }
  }
}
</script>
