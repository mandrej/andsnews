<template>
  <v-avatar
    size="36px"
    @click="signHandler">
    <img
      :src="user.photo"
      v-if="user.isAuthorized">
    <v-icon v-else flat color="secondary">account_circle</v-icon>
  </v-avatar>
</template>

<script>
import { mapState } from 'vuex'
import firebase from 'firebase'
import { FB } from '../../helpers/fire'

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
              photo: '',
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

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

</style>
