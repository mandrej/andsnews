<template>
  <div class="fullscreen text-center q-pa-md flex flex-center">
    <q-banner rounded inline-actions class="text-white bg-negative">
      <div class="text-h1">401</div>
      <div>Insufficient credentials...</div>
      <template v-slot:action>
        <q-btn flat color="white" size="xl" to="/">
          <q-icon left name="home" />
          <div>Go Home</div>
        </q-btn>
      </template>
    </q-banner>
  </div>
</template>
