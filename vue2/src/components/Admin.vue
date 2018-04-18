<template>
  <v-app light>
    <v-toolbar app>
      <v-icon @click="$router.push({name: 'home'})">arrow_back</v-icon>
      <v-toolbar-title>Admin</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn @click="submit" :disabled="!valid" color="primary">Submit</v-btn>
    </v-toolbar>

    <v-content>
      <v-container grid-list-md mt-3>
        <v-form v-model="valid" ref="form">
          <v-layout row wrap>
            <v-flex xs12 sm6 md4>
            </v-flex>
          </v-layout>
        </v-form>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import { mapState } from 'vuex'
// import firebase from 'firebase'

// const messaging = firebase.messaging()

export default {
  name: 'Admin',
  data: () => ({
    valid: true
  }),
  created () {
    this.$store.dispatch('getInfo')
  },
  computed: {
    ...mapState(['info'])
  },
  methods: {
    handleMessage () {
      // messaging.requestPermission()
      //   .then(() => console.log('success'))
      //   .catch(() => console.log('failed'))
    },
    submit () {
      // console.log(e.target.elements)
      if (this.$refs.form.validate()) {
        this.$store.dispatch('saveRecord', this.rec.safekey)
        this.$router.go(-1)
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

</style>
