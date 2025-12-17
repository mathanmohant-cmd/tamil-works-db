<template>
  <div class="about-page">
    <article class="about-content">
      <section aria-labelledby="journey">
        <h2 id="journey">Our journey</h2>
        <p>
          For many readers with only a basic grasp of Tamizh, the classical style of Sangam texts — and even their later commentaries — can feel daunting. A 12‑week introduction to Sangam literature by Mrs. Veidhei Herbert offered not only an accessible entry point but also revealed the richness of Tamizh poetry: its words, rhythms, and echoes across centuries.
        </p>
        <p>
          That experience sparked our desire to explore the words, themes, and ideas woven through this immense body of work. Mrs. Herbert’s bilingual resources, <a href="https://sangambyphone.wordpress.com/" target="_blank" rel="noopener noreferrer" class="inline-link">Sangam by Phone</a>, further opened doors for readers across languages.
        </p>
        <p>
          As we delved deeper, we discovered Prof. Dr. P. Pandiaraja's Tamizh Concordance, which presented the Sangam corpus with mathematical clarity. His Sangacholai resources became invaluable references in our journey.
        </p>
        <p>
          Through these efforts, we realised that Tamizh literature is not merely a treasure of the past — it is a living voice that continues to shape identity, culture, and imagination.
        </p>

      </section>

      <section aria-labelledby="why">
        <h2 id="why">Why we built this</h2>
        <p>
        By making it searchable, we hope to:
        </p>
        <ul class="list">
          <li>🔎 Help readers explore words and meanings across classical and modern texts.</li>
          <li>🌱 Spark new connections between roots, poems, and ideas.</li>
          <li>📚 Support learners, researchers, and enthusiasts in their journey.</li>
          <li>🌍 Invite a community to grow around Tamizh literature, keeping it alive for generations to come.</li>
        </ul>
        <p>
          We are also working on new tools to make exploring Sangam and Tamizh literature even easier, and look forward to sharing them soon.
        </p>
      </section>

      <section aria-labelledby="resources">
        <h2 id="resources">Resources</h2>
        <p>
          Explore these valuable resources from our inspirations:
        </p>
        <h3 class="resource-heading">Prof. Dr. P. Pandiaraja's Sangacholai</h3>
        <ul class="list resource-links">
          <li><a href="https://sangampedia.net/%e0%ae%9a%e0%ae%99%e0%af%8d%e0%ae%95%e0%ae%9a%e0%af%8d%e0%ae%9a%e0%af%8a%e0%ae%b2%e0%af%8d%e0%ae%b5%e0%ae%b3%e0%ae%ae%e0%af%8d/%e0%ae%9a%e0%ae%99%e0%af%8d%e0%ae%95%e0%ae%9a%e0%af%8d-%e0%ae%9a%e0%af%8a%e0%ae%b2%e0%af%8d%e0%ae%b5%e0%ae%b3%e0%ae%ae%e0%af%8d-2/" target="_blank" rel="noopener noreferrer">சங்கச் சொல்வளம்</a> — Sangam word treasury</li>
          <li><a href="https://sangampedia.net/%e0%ae%aa%e0%ae%a4%e0%af%8d%e0%ae%a4%e0%af%81%e0%ae%aa%e0%af%8d%e0%ae%aa%e0%ae%be%e0%ae%9f%e0%af%8d%e0%ae%9f%e0%af%81-%e0%ae%aa%e0%ae%a4%e0%af%8d%e0%ae%a4%e0%af%81%e0%ae%95%e0%af%8d%e0%ae%95%e0%ae%9f/" target="_blank" rel="noopener noreferrer">பத்துப்பாட்டு — பத்துக்கட்டுரைகள்</a> — Pattupattu articles</li>
        </ul>
        <h3 class="resource-heading">Mrs. Veidhei Herbert's Resources</h3>
        <ul class="list resource-links">
          <li><a href="https://sangambyphone.wordpress.com/" target="_blank" rel="noopener noreferrer">Sangam by Phone</a> — Bilingual Sangam literature resources</li>
        </ul>
      </section>

      <section class="invite" aria-labelledby="invitation">
        <h2 id="invitation">An invitation</h2>
        <p>
          This is not just our project — it can be yours too. We invite you to:
        </p>
        <ul class="list">
          <li>Use the tool to explore and learn.</li>
          <li>Share your ideas to make it better.</li>
          <li>Build more tools that bring Tamizh literature closer to today's readers.</li>
        </ul>
        <p>
          Every Tamizh work is part of a dialogue across time. We hope this platform becomes part of that dialogue, helping the voices of Tamizh literature reach new ears, new hearts, and new minds.
        </p>
        <h2 id="share">Share your ideas. Join the journey. Keep Tamizh literature alive</h2>
        <div class="cta" aria-label="Call to action">
          <a href="mailto:thamizh.words@gmail.com?subject=Tamizh%20Literature%20Search%20—%20Ideas" class="cta-button secondary">Contact Us</a>
        </div>
      </section>
    </article>
  </div>
</template>

<script>
export default {
  name: 'About'
}
</script>

<style scoped>
.about-page {
  padding: 2rem 1rem;
  max-width: 900px;
  margin: 0 auto;
}

.about-content {
  background: var(--surface);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  line-height: 1.7;
}

section {
  margin: 2rem 0 1rem;
  padding: 0;
}

section:first-child {
  margin-top: 0;
}

h2 {
  font-family: var(--english-font);
  font-size: 1.5rem;
  margin: 0 0 1rem;
  color: var(--primary-color);
  font-weight: 700;
}

h3.resource-heading {
  font-family: var(--english-font);
  font-size: 1.1rem;
  margin: 1.5rem 0 0.5rem;
  color: var(--text-primary);
  font-weight: 600;
}

p {
  margin: 0 0 1rem;
  color: var(--text-primary);
  font-size: 1.05rem;
  line-height: 1.7;
}

.list {
  margin: 1rem 0;
  padding-left: 1.5rem;
  list-style: none;
}

.list li {
  margin: 0.75rem 0;
  font-size: 1.05rem;
  color: var(--text-primary);
  line-height: 1.7;
}

.resource-links {
  margin: 0.5rem 0 1rem;
  padding-left: 2rem;
  list-style: disc;
}

.resource-links li {
  margin: 0.5rem 0;
}

.resource-links a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  font-family: var(--tamil-font), var(--english-font);
  font-size: 1.1rem;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.resource-links a:hover {
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

.inline-link {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.inline-link:hover {
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

.invite {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border: 2px solid var(--primary-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 2rem;
}

.cta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1.5rem;
  justify-content: center;
}

.cta-button {
  text-decoration: none;
  color: white;
  background: var(--primary-color);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(211, 47, 47, 0.3);
  font-size: 1rem;
}

.cta-button:hover {
  background: var(--primary-dark);
  box-shadow: 0 4px 10px rgba(211, 47, 47, 0.4);
  transform: translateY(-2px);
}

.cta-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(211, 47, 47, 0.3);
}

@media (max-width: 768px) {
  .about-content {
    padding: 1.5rem;
  }

  h2 {
    font-size: 1.3rem;
  }

  p, .list li {
    font-size: 1rem;
  }
}
</style>
