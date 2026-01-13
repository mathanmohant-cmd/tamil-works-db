<template>
  <div class="app-layout">
    <!-- Header persists across navigation - outside transition -->
    <AppHeader />
    <main class="app-content">
      <router-view v-slot="{ Component }">
        <!-- Transition only wraps content, not header -->
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="$route.path" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
// import AppHeader from '../components/AppHeader.vue' // OLD
import AppHeader from '../components/AppHeaderEnhanced.vue' // NEW Enhanced Header
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow-x: hidden; /* Prevent horizontal scroll */
  overflow-y: hidden; /* Prevent layout scroll (content scrolls instead) */
}


.app-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 1rem 2rem 2rem 2rem;
  position: relative; /* Establish stacking context for scrolling */
}

.app-content > * {
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

/* Transition for content area only */
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
