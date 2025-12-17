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
        <p class="closing">Join the Sangam of Tamizh literature admirers. Together, we can carry these voices into the future.</p>

        <div class="cta" aria-label="Call to action">
          <a href="mailto:thamizh.words@gmail.com?subject=Tamizh%20Literature%20Search%20—%20Ideas" class="cta-button secondary">Share your ideas</a>
        </div>
      </section>
    </article>

    <footer aria-label="Footer">
      Made with care for readers, learners, and technologists — honoring scholarship and inviting community.
    </footer>
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
  background: #ffffff;
  border: 1px solid #e6dccf;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.04);
  line-height: 1.7;
}

section {
  margin: 18px 0 8px;
  padding: 8px 0;
}

h2 {
  font-family: "Noto Serif Tamil", serif;
  font-size: 1.35rem;
  margin: 0 0 8px;
  color: #7a3e2f;
  font-weight: 600;
}

p {
  margin: 0 0 12px;
  color: #1a1a1a;
  font-size: 1rem;
}

.list {
  margin: 10px 0 8px;
  padding-left: 18px;
}

.list li {
  margin: 6px 0;
}

.invite {
  background: #f3e5dc;
  border: 1px solid #e6dccf;
  border-radius: 10px;
  padding: 16px;
  margin-top: 10px;
}

.closing {
  margin-top: 14px;
  font-weight: 600;
  color: #7a3e2f;
  text-align: center;
}

.cta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
  justify-content: center;
}

.cta-button {
  text-decoration: none;
  color: #7a3e2f;
  background: transparent;
  padding: 10px 14px;
  border-radius: 8px;
  font-weight: 600;
  border: 1px solid #7a3e2f;
  transition: all 0.3s ease;
}

.cta-button:hover {
  background: #7a3e2f;
  color: white;
  box-shadow: 0 2px 10px rgba(122, 62, 47, 0.25);
}

footer {
  margin-top: 24px;
  color: #4c4c4c;
  font-size: 0.9rem;
  text-align: center;
}

@media (max-width: 768px) {
  .about-content {
    padding: 18px;
  }
}
</style>
