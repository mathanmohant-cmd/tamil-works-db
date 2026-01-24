<template>
  <div>
    <!-- Role Selector Modal (shown when user hasn't selected a role) -->
    <RoleSelector v-if="needsRoleSelection" />

    <!-- Main App Content -->
    <router-view v-if="!needsRoleSelection" />
  </div>
</template>

<script setup>
import { useUserRole } from './composables/useUserRole.js'
import RoleSelector from './components/RoleSelector.vue'

const { needsRoleSelection } = useUserRole()
</script>

<style>
/* Global styles can go here if needed */
</style>
