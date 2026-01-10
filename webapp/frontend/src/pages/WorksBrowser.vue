<template>
  <div class="works-browser">
    <!-- Nested router view for all Works Browser pages -->
    <router-view />
  </div>
</template>

<script setup>
// WorksBrowser is a container component for nested routes:
// - /works (WorksList)
// - /works/:workId (WorkDetail)
// - /works/:workId/section/:sectionId (SectionView)
// - /works/:workId/verse/:verseId (VerseView)
</script>

<style scoped>
.works-browser {
  /* Container with no extra styling - let child components handle their layout */
  min-height: 100vh;
}
</style>
