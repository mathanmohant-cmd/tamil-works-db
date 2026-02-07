<template>
  <div class="welcome-page">
    <div class="container">
     <h3>&#x1F6E0;Beta Release</h3>
      <h1>Search Words in Tamil Literature</h1>
 
      <p class="tagline"><em>Explore words used across 2,000+ years of Tamil literary tradition</em></p>

      <div class="metrics">
        <span v-if="stats">{{ stats.total_works }} Thamizh literary works · {{ stats.total_verses.toLocaleString() }} verses · {{ stats.distinct_words.toLocaleString() }} words</span>
        <span v-else>Loading statistics...</span>
      </div>

      <router-link :to="{ name: 'QuickStart' }" class="button">👉 Start searching a word</router-link>

      <p>This tool shows every place a Thamizh word appears across classical literature — with the full verse and context. It helps you understand how words are actually used, not just what they mean.</p>

      <h2>How it works</h2>
      <ul>
        <li>Every verse is carefully broken into words</li>
        <li>Each word remembers its source</li>
        <li>Your search scans millions of stored words</li>
        <li>Results show verses, authors, and context</li>
      </ul>

      <p class="note">Built using trusted concordance data from Prof. P. Pandiyaraja (<a href="http://tamilconcordance.in" target="_blank" rel="noopener noreferrer">tamilconcordance.in</a>)</p>

      <h2>Example</h2>
      <p>Search <strong>"காதல்"</strong> and discover:</p>
      <ul>
        <li>Where it appears</li>
        <li>How Sangam poets used it</li>
        <li>How devotional poets reimagined it</li>
      </ul>
      <p><em>You're not just learning a word — you're seeing Thamizh thought evolve.</em></p>

      <h2>Powerful search features</h2>
      <ul>
        <li>Exact & partial word search</li>
        <li>Filter by literary work</li>
        <li>Browse by historical collection</li>
        <li>Export results for study</li>
      </ul>

      <h2>Why this matters</h2>
      <p>A dictionary explains words. A concordance reveals meaning through use.</p>
      <p>This tool is your gateway to Thamizh literary heritage.</p>

      <h2>Who is this for?</h2>
      <div class="who-grid">
        <div class="who-item">🎓 <strong>Students</strong><br>Learn words in real sentences.</div>
        <div class="who-item">📚 <strong>Researchers</strong><br>Analyze usage across texts.</div>
        <div class="who-item">❤️ <strong>Thamizh lovers</strong><br>Discover hidden verses.</div>
        <div class="who-item">✍️ <strong>Writers & teachers</strong><br>Explore authentic usage.</div>
      </div>
      <!--
      <h2>🚀 What's coming next</h2>
      <ul class="future-list">
        <li>Word root & grammar analysis</li>
        <li>Thamizh–English translations</li>
        <li>Thematic search (love, rain, virtue…)</li>
        <li>Author comparisons</li>
        <li>Audio pronunciation</li>
        <li>Commentaries</li>
        <li>Personal notes & saved verses</li>
        <li>Visualizations & timelines</li>
      </ul>
      -->
    </div>
  </div>
</template>

<script setup>
import { useStats } from '../../../composables/useStats.js'

// Get stats from composable
const { stats, loadStats } = useStats()

// Load stats if not already loaded
if (!stats.value) {
  loadStats()
}
</script>

<style scoped>
.welcome-page {
  font-family: var(--tamil-font), var(--english-font);
  background: #ffffff;
  color: #222;
  line-height: 1.6;
  min-height: calc(100vh - 200px);
}

.container {
  max-width: 820px;
  margin: 0 auto;
  padding: 40px 20px 60px;
}

h1, h2 {
   font-family: var(--tamil-font), var(--english-font);
  font-weight: 600;
  margin-bottom: 12px;
  color: #111;
}

h1 {
  font-size: 32px;
  margin-top: 0;
}

h2 {
  font-size: 22px;
  margin-top: 32px;
}

.tagline {
  margin-bottom: 16px;
  font-size: 17px;
}

p {
  margin-bottom: 16px;
  font-size: 17px;
}

.metrics {
  font-size: 15px;
  margin-bottom: 20px;
}

.button {
  display: inline-block;
  padding: 10px 18px;
  background: #333;
  color: #fff;
  text-decoration: none;
  border-radius: 4px;
  font-size: 15px;
  margin: 12px 0 20px;
  transition: background 0.2s;
}

.button:hover {
  background: #555;
}

ul {
  margin: 0 0 16px 20px;
  padding: 0;
  font-size: 16px;
}

.note {
  font-size: 14px;
  margin-top: 6px;
}

.note a {
  color: #333;
  text-decoration: none;
  border-bottom: 1px solid #999;
}

.note a:hover {
  color: #000;
  border-bottom-color: #333;
}

.who-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.who-item {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fafafa;
  font-size: 15px;
}

.future-list {
  columns: 2;
  column-gap: 24px;
  font-size: 15px;
}

.future-list li {
  margin-bottom: 6px;
  break-inside: avoid;
}

@media (max-width: 600px) {
  .container {
    padding: 20px 15px 40px;
  }

  h1 {
    font-size: 26px;
  }

  h2 {
    font-size: 20px;
  }

  .future-list {
    columns: 1;
  }

  .who-grid {
    grid-template-columns: 1fr;
  }
}
</style>
