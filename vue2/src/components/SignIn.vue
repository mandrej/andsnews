<template>
  <v-btn v-if="user.isAuthorized" @click="signHandler" flat color="secondary">Sign-Off</v-btn>
  <v-btn v-else @click="signHandler" flat color="primary">Sign-In</v-btn>
</template>

<script>
import { mapState } from 'vuex'
import firebase from 'firebase'
import { FB } from '../main'

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
    ...mapState(['user'])
  },
  methods: {
    signHandler () {
      if (this.user.uid) {
        FB.auth().signOut()
          .then(() => {
            this.$store.dispatch('signIn', {
              name: '',
              email: '',
              uid: null,
              isAuthorized: false,
              isAdmin: false
            })
          })
      } else {
        FB.auth().signInWithPopup(provider)
          .then(response => {
            this.$store.dispatch('signIn', {
              name: response.user.displayName,
              email: response.user.email,
              uid: response.user.uid,
              isAuthorized: true,
              isAdmin: (this.admins.indexOf(response.user.uid) !== -1)
            })
          })
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

</style>
