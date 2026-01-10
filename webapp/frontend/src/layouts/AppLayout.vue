<template>
  <div class="app-layout">
    <AppHeader />
    <main class="app-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import AppHeader from '../components/AppHeader.vue'
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}


.app-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 1rem 2rem 2rem 2rem;
}

.app-content > * {
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .app-content {
    padding: 0.5rem 1rem 1rem 1rem;
  }
}
</style>
