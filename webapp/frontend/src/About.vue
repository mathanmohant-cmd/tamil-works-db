<template>
  <div class="about-page">
    <article class="about-content">
      <section aria-labelledby="journey">
        <h2 id="journey">My journey</h2>
        <p>
          My journey into Tamil literature began through the Chicago Tamil Sangam community. A paper presented in the 5th International Conference on Thirukkural gave me a glimpse of how the seeds sown by Thirukkural continue to shape our thoughts even today. I wished I had known Tholkappiyam, Thirukkural, Sangam Literature, Silapathikaram, and Kambaramayanam earlier, for these works constitute the very core of Tamil literature.
        </p>
        <p>
          It might have remained just a wish, but the network of people I met through CTS led me to the Introduction to Sangam Literature course conducted by Mrs. Vaidehi Herbert. For many Tamils like me, who attended schools in English medium with only a basic grasp of Tamizh, the classical style of Sangam texts — and even their later commentaries — can feel daunting. Her 12‑week course offered not only an accessible entry point but also revealed the richness of Tamizh poetry: its words, rhythms, and echoes across centuries. Her students — many of them experts themselves — joined weekly learning sessions, guiding other hand‑in‑hand into the fascinating world of the Sangam era.
        </p>
        <p>
          As I delved deeper, I discovered Prof. Dr. P. Pandiaraja's Tamizh Concordance, which presented the Sangam corpus with mathematical clarity. His Sangacholai resources opened perspectives that extended beyond literary beauty, revealing new dimensions of structure and meaning.
        </p>
        <p>
          The erudite exposition of Tholkappiyam and Silapathikaram by Prof. Dr. Ku. Ve. Balasubramanian expanded my horizons and strengthened my confidence to explore the words, themes, and ideas woven through these invaluable collections of work.
        </p>
        <p>
          These exemplars — தமிழ்ச் சான்றோர், as Thiruvalluvar would call them — had shown Sangam literature is not merely a treasure of the past; it is a living voice that continues to shape identity, culture, and imagination.
        </p>
      </section>

      <section aria-labelledby="why">
        <h2 id="why">Why I built this</h2>
        <p>
          When reading through these works, I noticed links between words, for example
        </p>
        <ul class="list">
          <li>பா, பாய், பாட்டு, பாம்பு - Extend, spread</li>
          <li>கல், கல்வி, கற்பு - Complete, Steadfast</li>
          <li>யா, யாமம், யானை, யாணர் - Dark, Unknown, New</li>
          <li>எல், எல்லை, எல்லன் - Visible, illuminated</li>
        </ul>
        <p>
          To indulge in exploring these connections further, I wanted a search tool that can find the usage of words across many works. By making Sangam and other Tamizh literature searchable, I also hope to:
        </p>
        <ul class="list">
          <li>🔎 Help readers explore words and meanings across classical and modern texts.</li>
          <li>🌱 Spark new connections between roots, poems, and ideas.</li>
          <li>📚 Support learners, researchers, and enthusiasts in their journey.</li>
          <li>🌍 Invite a community to grow around Tamizh literature.</li>
        </ul>
      </section>

      <section class="invite" aria-labelledby="invitation">
        <h2 id="invitation">An invitation</h2>
        <p>
          Even though I use "My Journey", "Why I built", this is a collective effort. Without the work of others, I wouldn't even dare to start something like this. In a way this is not just my project — it can be yours too. I invite you to:
        </p>
        <ul class="list">
          <li>Use the tool to explore and learn.</li>
          <li>Share your ideas to make it better.</li>
          <li>Build more tools that bring Tamizh literature closer to today's readers.</li>
        </ul>
        <p>
          Every Tamizh work is part of a dialogue across time. I hope this platform becomes part of that dialogue, helping the voices of Tamizh literature reach new ears, new hearts, and new minds.
        </p>
        <h2 id="share">Share your ideas. Join the journey.</h2>
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
