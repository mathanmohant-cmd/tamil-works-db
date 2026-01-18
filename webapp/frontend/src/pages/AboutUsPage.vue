<template>
  <div class="static-page">
    <div class="page-container">
      <h1>About Us</h1>

      <section class="content-section">
        <h2>Our Mission</h2>
        <p>Thamizh Word Explorer is dedicated to making classical Tamil literature accessible and searchable for everyone—from students and researchers to lovers of Tamil language and culture.</p>

        <p>We believe that Tamil literary heritage should be easy to explore and understand. This tool brings together thousands of years of literature into one searchable database, allowing you to discover how words and ideas have evolved across centuries.</p>
      </section>

      <section class="content-section">
        <h2>What We Do</h2>
        <p>Our platform provides:</p>
        <ul>
          <li><strong>Comprehensive Word Search:</strong> Find every occurrence of any Tamil word across classical literature</li>
          <li><strong>Contextual Understanding:</strong> See complete verses and contexts, not just definitions</li>
          <li><strong>Historical Perspective:</strong> Track how words and concepts evolved across different periods and works</li>
          <li><strong>Scholarly Research Tools:</strong> Export results, filter by works, and analyze usage patterns</li>
        </ul>
      </section>

      <section class="content-section">
        <h2>Acknowledgments</h2>
        <p>This project is built upon the comprehensive concordance work of <strong>Prof. Dr. P. Pandiyaraja</strong>, available at <a href="http://tamilconcordance.in" target="_blank" rel="noopener noreferrer">tamilconcordance.in</a>. His meticulous compilation and word segmentation principles form the foundation of our database.</p>

        <p>We are grateful for his dedication to preserving and making Tamil literature accessible to the world.</p>
      </section>

      <section class="content-section">
        <h2>Our Vision</h2>
        <p>We envision a future where:</p>
        <ul>
          <li>Tamil literary heritage is easily accessible to learners worldwide</li>
          <li>Researchers can conduct sophisticated analysis across the entire Tamil canon</li>
          <li>New generations discover the beauty and depth of classical Tamil literature</li>
          <li>Technology serves to preserve and promote cultural and linguistic heritage</li>
        </ul>
      </section>

      <section class="content-section">
        <h2>Join Our Journey</h2>
        <p>This is an evolving project. We're continuously adding more works, improving search capabilities, and developing new features to better serve the Tamil literary community.</p>

        <p>If you have suggestions, corrections, or would like to contribute, we'd love to hear from you. Visit our <router-link :to="{ name: 'ContactUs' }">Contact Us</router-link> page to get in touch.</p>
      </section>

      <div class="back-link">
        <router-link :to="{ name: 'Home' }">← Back to Home</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// Static About Us page
</script>

<style scoped>
.static-page {
  padding: 2rem 1rem;
  max-width: 900px;
  margin: 0 auto;
}

.page-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin: 0 0 2rem 0;
  border-bottom: 3px solid var(--primary-color);
  padding-bottom: 1rem;
}

.content-section {
  margin: 2rem 0;
}

.content-section h2 {
  font-size: 1.6rem;
  color: var(--secondary-color);
  margin: 0 0 1rem 0;
  font-weight: 600;
}

.content-section p {
  line-height: 1.7;
  color: var(--text-primary);
  margin: 1rem 0;
  font-size: 1.05rem;
  text-align: justify;
}

.content-section ul {
  margin: 1rem 0;
  padding-left: 2rem;
}

.content-section li {
  margin: 0.75rem 0;
  line-height: 1.6;
  color: var(--text-primary);
}

.content-section a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px dotted rgba(25, 118, 210, 0.3);
}

.content-section a:hover {
  border-bottom: 1px solid var(--secondary-color);
}

.back-link {
  margin-top: 3rem;
  text-align: center;
}

.back-link a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  padding: 0.75rem 1.5rem;
  border: 2px solid var(--secondary-color);
  border-radius: 6px;
  display: inline-block;
  transition: all 0.3s ease;
}

.back-link a:hover {
  background: var(--secondary-color);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(25, 118, 210, 0.2);
}

@media (max-width: 768px) {
  .static-page {
    padding: 1rem 0.5rem;
  }

  .page-container {
    padding: 1.5rem;
  }

  h1 {
    font-size: 2rem;
  }

  .content-section h2 {
    font-size: 1.3rem;
  }

  .content-section p,
  .content-section li {
    font-size: 1rem;
  }
}
</style>
