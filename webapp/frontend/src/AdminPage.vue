<template>
  <div class="admin-wrapper">
    <Admin />
  </div>
</template>

<script>
import Admin from './Admin.vue'

export default {
  name: 'AdminPage',
  components: {
    Admin
  }
}
</script>

<style scoped>
.admin-wrapper {
  min-height: 100vh;
  background-color: #f5f5f5;
}
</style>
