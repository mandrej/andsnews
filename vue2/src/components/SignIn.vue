<template>
  <v-avatar
    size="36px"
    @click="signHandler"
    style="cursor: pointer">
    <img
      v-if="photoUrl"
      :src="photoUrl">
    <v-icon v-else flat>account_circle</v-icon>
  </v-avatar>
</template>

<script>
import { mapState } from 'vuex'
import { FB } from '@/helpers/fire'
import { EventBus } from '@/helpers/event-bus'
import firebase from 'firebase/app'
import 'firebase/app'
import 'firebase/auth'

const provider = new firebase.auth.GoogleAuthProvider().addScope('email')

export default {
  name: 'SignIn',
  data: () => ({
    // milan, mihailo
    admins: [
      'j8ezW5PBwMMnzrUvDA9ucYOOmrD3',
      'vlRwHqVZNfOpr3FRqQZGqT2M2HA2'
    ],
    photoUrl: null
  }),
  mounted () {
    if (this.user && this.user.photo) {
      this.photoUrl = this.user.photo
    }
    EventBus.$on('signin', user => {
      if (user && user.photo) {
        this.photoUrl = user.photo
      } else {
        this.photoUrl = null
      }
    })
  },
  computed: {
    ...mapState('All', ['user'])
  },
  methods: {
    signHandler () {
      if (this.user && this.user.uid) {
        FB.auth().signOut()
          .then(() => {
            this.photoUrl = null
            this.$store.dispatch('All/saveUser', {
              name: '',
              email: '',
              uid: null,
              photo: '',
              isAuthorized: false,
              isAdmin: false
            })
            this.$router.push({ name: 'home' })
          })
      } else {
        FB.auth().signInWithPopup(provider)
          .then(response => {
            this.$store.dispatch('All/saveUser', {
              name: response.user.displayName,
              email: response.user.email,
              uid: response.user.uid,
              photo: response.user.photoURL,
              isAuthorized: true,
              isAdmin: (this.admins.indexOf(response.user.uid) !== -1)
            })
          })
      }
    }
  }
}
</script>
