<template>
  <div>
    <Message>></Message>
    <v-app>
      <slot name="drawer"></slot>
      <slot name="appbar"></slot>
      <v-content class="accent">
        <slot></slot>
      </v-content>
    </v-app>
  </div>
</template>

<script>
export default {
  name: 'Layout',
  components: {
    'Message': () => import(/* webpackChunkName: "message" */ '@/components/Message')
  }
}
</script>

