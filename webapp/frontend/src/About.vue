<template>
  <div class="about-page">
    <article class="about-content">
      <section aria-labelledby="journey">
        <h2 id="journey">Our journey</h2>
        <p>
          This project began with curiosity. A 12‑week introduction to Sangam literature by Mrs. Veidhei Herbert opened our eyes to the richness of Tamizh poetry — its words, rhythms, and echoes across centuries. That experience led us to explore not just Sangam texts, but the vast and diverse world of Tamizh literature: from classical works to modern voices, from poetry to prose, from epics to everyday expressions.
        </p>
        <p>
          We wanted a way to trace words, themes, and ideas across this immense tradition. That search led us to the pioneering work of scholars like Dr. P. Pandiaraja, whose dedication made the Sangam corpus accessible. Building on that inspiration, we created a tool to make Tamizh literature searchable, discoverable, and alive for today's readers.
        </p>
      </section>

      <section aria-labelledby="why">
        <h2 id="why">Why we built this</h2>
        <p>
          Tamizh literature is not just a treasure of the past — it is a living voice that continues to shape identity, culture, and imagination. By making it searchable, we hope to:
        </p>
        <ul class="list">
          <li>🔎 Help readers explore words and meanings across classical and modern texts.</li>
          <li>🌱 Spark new connections between roots, poems, and ideas.</li>
          <li>📚 Support learners, researchers, and enthusiasts in their journey.</li>
          <li>🌍 Invite a community to grow around Tamizh literature, keeping it alive for generations to come.</li>
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

        <div class="cta" aria-label="Call to action">
          <a href="mailto:thamizh.words@gmail.com?subject=Tamizh%20Literature%20Search%20—%20Ideas" class="cta-button secondary">Share your ideas</a>
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
