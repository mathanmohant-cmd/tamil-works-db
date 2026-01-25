<template>
  <div class="app-layout">
    <!-- Header persists across navigation - outside transition -->
    <AppHeader />
    <main class="app-content">
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <!-- Transition only wraps content, not header -->
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="$route.path" />
          </transition>
        </router-view>
      </div>
      <!-- Footer scrolls with content, at bottom when content is short -->
      <AppFooter />
    </main>
  </div>
</template>

<script setup>
// import AppHeader from '../components/AppHeader.vue' // OLD
import AppHeader from '../components/AppHeaderEnhanced.vue' // NEW Enhanced Header
import AppFooter from '../components/AppFooter.vue'
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow-x: hidden;
  overflow-y: hidden;
}

.app-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.content-wrapper {
  flex: 1;
  padding: 1rem 2rem 2rem 2rem;
}

.content-wrapper > * {
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
  .content-wrapper {
    padding: 0.5rem 1rem 1rem 1rem;
  }
}
</style>
