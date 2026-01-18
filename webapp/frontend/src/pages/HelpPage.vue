<template>
  <div class="help-page">
    <div class="help-container">
      <h1>Help & Documentation</h1>
      <p class="subtitle">Learn how to use the Tamil Literary Concordance Search</p>

      <div class="help-cards">
        <router-link :to="{ name: 'QuickStart' }" class="help-card">
          <div class="card-icon">🚀</div>
          <h2>Quick Start</h2>
          <p>Start searching for Tamil words across classical literature</p>
        </router-link>

        <router-link :to="{ name: 'UnderstandingThisTool' }" class="help-card">
          <div class="card-icon">💡</div>
          <h2>Understanding This Tool</h2>
          <p>Learn what a concordance is and how this tool works</p>
        </router-link>

        <router-link :to="{ name: 'WordSegmentation' }" class="help-card">
          <div class="card-icon">📝</div>
          <h2>Word Segmentation Principles</h2>
          <p>Understand how Tamil words are segmented for accurate search</p>
        </router-link>

        <router-link :to="{ name: 'TransliterationGuide' }" class="help-card">
          <div class="card-icon">⌨️</div>
          <h2>Transliteration Guide</h2>
          <p>Learn how to type Tamil letters using English keyboard (A→அ)</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// No specific logic needed for this landing page
</script>

<style scoped>
.help-page {
  min-height: calc(100vh - 200px);
}

.help-container {
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

.help-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-top: 32px;
}

.help-card {
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

.help-card:hover {
  border-color: #4a90e2;
  box-shadow: 0 8px 24px rgba(74, 144, 226, 0.15);
  transform: translateY(-4px);
}

.card-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.help-card h2 {
  font-size: 22px;
  color: #111;
  margin-bottom: 12px;
  font-weight: 600;
}

.help-card p {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

@media (max-width: 768px) {
  .help-container {
    padding: 24px 16px;
  }

  h1 {
    font-size: 26px;
  }

  .subtitle {
    font-size: 16px;
  }

  .help-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .help-card {
    padding: 24px 20px;
  }

  .card-icon {
    font-size: 40px;
  }

  .help-card h2 {
    font-size: 20px;
  }

  .help-card p {
    font-size: 15px;
  }
}
</style>
