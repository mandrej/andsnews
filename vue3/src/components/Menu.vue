<template>
  <q-list>
    <q-item clickable @click="auth.signIn">
      <q-item-section avatar>
        <q-icon name="person" />
      </q-item-section>

      <q-item-section v-if="user.name">
        <q-item-label>Sign out</q-item-label>
        <q-item-label caption>{{ user.name }}</q-item-label>
      </q-item-section>
      <q-item-section v-else>
        <q-item-label>Sign in</q-item-label>
        <q-item-label caption>using your Google account</q-item-label>
      </q-item-section>
    </q-item>

    <q-item v-show="user.isAuthorized" to="/add">
      <q-item-section avatar>
        <q-icon name="add_circle" />
      </q-item-section>

      <q-item-section>
        <q-item-label>Add</q-item-label>
        <q-item-label caption>jpeg images less then 4 Mb</q-item-label>
      </q-item-section>
    </q-item>

    <q-item v-show="user.isAdmin" to="/admin">
      <q-item-section avatar>
        <q-icon name="settings" />
      </q-item-section>

      <q-item-section>
        <q-item-label>Admin</q-item-label>
        <q-item-label caption>rebuild various counters</q-item-label>
      </q-item-section>
    </q-item>
    <q-item />
  </q-list>
</template>

<script setup>
import { computed } from "vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const user = computed(() => auth.user);
</script>
