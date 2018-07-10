<template>
  <v-avatar
    size="36px"
    @click="signHandler">
    <img
      v-if="photoUrl"
      :src="photoUrl">
    <v-icon v-else flat>account_circle</v-icon>
  </v-avatar>
</template>

<script>
import { mapState } from 'vuex'
import { FB } from '@/helpers/fire'
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
    ]
  }),
  computed: {
    ...mapState('All', ['user']),
    photoUrl () {
      if (this.user && this.user.photo) {
        return this.user.photo
      }
    }
  },
  methods: {
    signHandler () {
      if (this.user.uid) {
        FB.auth().signOut()
          .then(() => {
            this.$store.dispatch('All/saveUser', {
              name: '',
              email: '',
              uid: null,
              photo: '',
              isAuthorized: false,
              isAdmin: false
            })
            this.$router.push({name: 'home'})
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

<style scoped>
.v-avatar {
  cursor: pointer;
}
</style>
