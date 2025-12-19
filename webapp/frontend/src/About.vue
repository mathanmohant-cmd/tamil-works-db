<template>
  <div class="about-page">
    <article class="about-content">
      <section aria-labelledby="journey">
        <h2 id="journey">My Journey</h2>
        <p>
          My journey into Tamizh literature began within the Chicago Tamil Sangam community. A paper presented at the 5th International Conference on Thirukkural offered a glimpse into how the ideas sown by Thirukkural continue to shape thought and values even today. It also awakened a desire to learn works such as <em>Tholkappiyam, Thirukkural, Sangam Literature, Silapathikaram,</em> and <em>Kambaramayanam</em> - the very foundation of Tamizh literary and cultural consciousness.
        </p>
        <p>
          What might have remained a dormant wish became possible through the people and learning communities I encountered along the way. A defining moment was the <em>Introduction to Sangam Literature</em> course conducted by Mrs. Vaidehi Herbert. For many Tamils educated primarily in English, engaging with classical Tamizh texts—and even their traditional commentaries—can feel daunting. Her twelve-week course opened an accessible doorway into Sangam poetry, revealing the richness of Tamizh language, rhythm, imagery, and resonance across centuries. Weekly discussions—shaped by fellow learners and scholars—became a shared space of inquiry and discovery.
        </p>
        <p>
          As my exploration broadened, I encountered the Tamizh Concordance developed by Prof. Dr. P. Pandiaraja and the Sangacholai resources, which presented the Sangam corpus with remarkable structural and analytical clarity. These works showed that Tamizh literature is not only aesthetically powerful but also profoundly systematic, revealing patterns and relationships that span texts and time.
        </p>
        <p>
          Further guidance came through the erudite expositions of Prof. Dr. Ku. Ve. Balasubramanian on <em>Tholkappiyam</em> and <em>Silapathikaram</em>. His teachings strengthened my confidence to engage deeply with Tamizh words, themes, and ideas—and reinforced the understanding that this tradition thrives through careful study, dialogue, and transmission.
        </p>
        <p>
          These teachers and scholars—தமிழ்ச் சான்றோர், as Thiruvalluvar would call them—made one truth clear: Sangam literature is not a relic of the past. It is a living voice, sustained by communities of readers, learners, and interpreters across generations.
        </p>
      </section>

      <section aria-labelledby="wish">
        <h2 id="wish">My Wish</h2>
        <p>
          In spite of immense support, I feel my journey has just begun. When I read the texts, sometimes words and usages jump out and begin to tease—inviting me into a search for meaning and connection. For example:
        </p>
        <ul class="list">
          <li><strong>பா, பாய், பாட்டு, பாம்பு</strong> – That spreads, expands</li>
          <li><strong>கல், கல்வி, கற்பு</strong> – Strong, Complete Knowledge, Steadfast</li>
          <li><strong>யா, யாமம், யானை, யாணர்</strong> – Black, Dark, Unknown, Novel</li>
          <li><strong>எல், எல்லை, எல்லன்</strong> – Visible, illuminated</li>
        </ul>
        <p>
          I am not an expert to make a definite call, but I wanted to indulge in this puzzle. That is why I began to envision a tool that could search across works, with quick access to etymological dictionaries and reference to expert commentaries. At the moment, I have only added a search facility. I hope the rest can be added too. With AI tools, the chance of building an integrated platform is high.
        </p>
      </section>

      <section aria-labelledby="hope">
        <h2 id="hope">My Hope</h2>
        <p>
          Together, we aim to:
        </p>
        <ul class="list">
          <li>🔎 Enable exploration of words, roots, and meanings across classical and modern Tamizh texts.</li>
          <li>🌱 Encourage new connections between language, poetry, and ideas.</li>
          <li>📚 Support learners, researchers, and enthusiasts at every stage.</li>
          <li>🌍 Nurture a community committed to keeping Tamizh literature alive and accessible.</li>
        </ul>
      </section>

      <section class="invite" aria-labelledby="invitation">
        <h2 id="invitation">An Invitation</h2>
        <p>
          While this platform began with my personal journey, it exists because of collective effort—built upon the scholarship, teaching, and generosity of many before us. This space grows through participation. I invite you to:
        </p>
        <ul class="list">
          <li>Explore Tamizh literature using these tools.</li>
          <li>Share insights, corrections, and ideas.</li>
          <li>Contribute new approaches that bring classical texts closer to today's readers.</li>
        </ul>
        <p>
          Every Tamizh work is part of a dialogue across time. I hope this platform becomes part of that dialogue—connecting past and present, individual curiosity and shared understanding.
        </p>
        <h2 id="share">Share your ideas. Join the journey.</h2>
        <div class="cta" aria-label="Call to action">
          <a href="mailto:thamizh.words@gmail.com?subject=Tamizh%20Literature%20Search%20—%20Ideas" class="cta-button secondary">Join Us</a>
        </div>
      </section>

      <footer class="gratitude-footer">
        <p class="gratitude-text">
          Written in gratitude to the தமிழ்ச் சான்றோர் who made this journey possible.
        </p>
        <p class="author-name">— T. Mathan Mohan</p>
      </footer>
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

.gratitude-footer {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 2px solid var(--border-color);
  text-align: center;
}

.gratitude-text {
  font-size: 1.1rem;
  font-style: italic;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  font-family: var(--tamil-font), var(--english-font);
}

.author-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary-color);
  margin-top: 0.5rem;
  margin-bottom: 0;
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

  .gratitude-text {
    font-size: 1rem;
  }

  .author-name {
    font-size: 0.95rem;
  }
}
</style>
