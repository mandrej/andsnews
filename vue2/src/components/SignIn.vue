<template>
  <v-avatar
    size="36px"
    @click="signHandler"
    style="cursor: pointer"
    transition="fade-transition" mode="out-in"
    >
    <img
      v-if="photoUrl"
      :src="photoUrl">
    <v-icon v-else>account_circle</v-icon>
  </v-avatar>
</template>

<script>
import { mapState } from 'vuex'
import { EventBus } from '@/helpers/event-bus'
import FIREBASEAPP from '@/helpers/fire'
import firebase from '@firebase/app'
import '@firebase/auth'

const provider = new firebase.auth.GoogleAuthProvider().addScope('email')

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
      this.photoUrl = user && user.photo
    })
  },
  methods: {
    signHandler () {
      if (this.user && this.user.uid) {
        FIREBASEAPP.auth().signOut()
          .then(() => {
            this.$store.dispatch('auth/saveUser', {})
            this.$router.push({ name: 'home' })
          })
      } else {
        FIREBASEAPP.auth().signInWithPopup(provider)
          .then(response => {
            this.$store.dispatch('auth/saveUser', {
              name: response.user.displayName,
              email: response.user.email,
              uid: response.user.uid,
              photo: response.user.photoURL,
              isAuthorized: true,
              isAdmin: (this.$admins.indexOf(response.user.uid) !== -1)
            })
          })
      }
    }
  }
}
</script>
