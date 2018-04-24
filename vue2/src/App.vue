<template>
  <div id="app">
    <router-view :version="version.match(/.{1,4}/g).join('.')"/>
  </div>
</template>

<script>
export default {
  name: 'App',
  data: () => ({
    version: '201804242054'
  })
}
</script>

<style>
#app {
  font-family: 'Roboto', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
