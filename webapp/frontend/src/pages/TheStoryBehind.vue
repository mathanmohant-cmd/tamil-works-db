<template>
  <div class="story-page">
    <div class="story-container">
      <h1>The Story Behind</h1>
      <p class="subtitle">Learn about the journey and inspiration behind this platform</p>

      <div class="story-cards">
        <router-link :to="{ name: 'Journey' }" class="story-card">
          <div class="card-icon">🌱</div>
          <h2>The Idea Behind This Project</h2>
          <p>How curiosity about Tamil words led to building this search platform</p>
        </router-link>

        <router-link :to="{ name: 'Inspiration' }" class="story-card">
          <div class="card-icon">🙏</div>
          <h2>Inspiring Exemplars</h2>
          <p>The scholars and mentors whose work made this platform possible</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// No specific logic needed for this landing page
</script>

<style scoped>
.story-page {
  min-height: calc(100vh - 200px);
}

.story-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

h1 {
  font-size: 32px;
  color: #111;
  margin-bottom: 8px;
  font-weight: 600;
}

.subtitle {
  font-size: 18px;
  color: #666;
  margin-bottom: 40px;
}

.story-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-top: 32px;
}

.story-card {
  display: block;
  padding: 32px 24px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
  cursor: pointer;
}

.story-card:hover {
  border-color: #4a90e2;
  box-shadow: 0 8px 24px rgba(74, 144, 226, 0.15);
  transform: translateY(-4px);
}

.card-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.story-card h2 {
  font-size: 22px;
  color: #111;
  margin-bottom: 12px;
  font-weight: 600;
}

.story-card p {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

@media (max-width: 768px) {
  .story-container {
    padding: 24px 16px;
  }

  h1 {
    font-size: 26px;
  }

  .subtitle {
    font-size: 16px;
  }

  .story-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .story-card {
    padding: 24px 20px;
  }

  .card-icon {
    font-size: 40px;
  }

  .story-card h2 {
    font-size: 20px;
  }

  .story-card p {
    font-size: 15px;
  }
}
</style>
