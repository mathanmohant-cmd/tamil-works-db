<template>
  <div class="about-page">
    <article class="about-content">
      <section aria-labelledby="journey">
        <h2 id="journey">My Journey</h2>
        <p class="author-name">— T. Mathan Mohan</p>
        <p>
          It started within the Chicago Tamizh Sangam community. A paper presented at the 5th International Conference on Thirukkural offered an early glimpse into how the ideas sown by the Thirukkural continue to shape thought and values even today.
        </p>
        <p>
          It also awakened a desire to engage more deeply with works such as <em>Tholkappiyam, Thirukkural, Sangam Literature, Silapathikaram,</em> and <em>Kambaramayanam</em>—the foundational texts of Tamizh literary and cultural consciousness.
        </p>
        <p>
          What might have remained a dormant wish became possible through the people and learning communities I encountered along the way. A defining moment was the <em>Introduction to Sangam Literature</em> course conducted by Ms. Vaidehi Herbert.
        </p>
        <p>
          For many Tamizhs educated primarily in English, approaching classical Tamizh texts—and even their traditional commentaries—can feel daunting. Her twelve-week course opened an accessible doorway into Sangam poetry, revealing the richness of the Tamizh language: its rhythm, imagery, and resonance across centuries. Weekly discussions, shaped by fellow learners and scholars, became a shared space of inquiry and discovery.
        </p>
        <p>
          As my exploration broadened, I encountered the Tamizh Concordance developed by Prof. P. Pandiaraja and the Sangacholai resources, which present the Sangam corpus with remarkable structural and analytical clarity. These works revealed that Tamizh literature is not only aesthetically powerful but also profoundly systematic—uncovering patterns and relationships that span texts and time.
        </p>
        <p>
          Further guidance came through the erudite expositions of Prof. Ku. Ve. Balasubramanian on <em>Tholkappiyam</em> and <em>Silapathikaram</em>. His teachings strengthened my confidence to work closely with Tamizh words, themes, and ideas, and reinforced the understanding that this tradition thrives through careful study, dialogue, and transmission.
        </p>
        <p>
          These teachers and scholars—தமிழ்ச் சான்றோர், as Thiruvalluvar would call them—made one truth clear: Sangam literature is not a relic of the past. It is a living voice, sustained by communities of readers, learners, and interpreters across generations.
        </p>
        <p>
          Together, these experiences shaped a personal commitment to reading slowly, attentively, and with genuine curiosity.
        </p>
        <p>
          When reading the texts, certain words and usages often stand out and spark curiosity—prompting a pause, comparison, and a return to the text with fresh questions.
        </p>
        <p>
          For example:
        </p>
        <ul class="list">
          <li><strong>பா, பாய், பாட்டு, பாம்பு</strong> – ideas of spreading and expansion</li>
          <li><strong>கல், கல்வி, கற்பு</strong> – strength, learning, steadiness</li>
          <li><strong>யா, யாமம், யானை, யாணர்</strong> – darkness, the unfamiliar, the new</li>
          <li><strong>எல், எல்லை, எல்லன்</strong> – visibility and boundary</li>
        </ul>
        <p>
          These are moments of discovery that many readers encounter while engaging with the texts. Yet following such threads across poems, genres, and commentaries can be difficult without simple ways to search and compare.
        </p>
        <p>
          This platform grew out of that need. At present, it offers a basic search across selected works, helping readers locate words and usages more easily. Over time, additional references and tools may be added to support deeper exploration. The aim remains careful reading rather than quick conclusions.
        </p>
        <p>
          The path through classical Tamizh literature is rarely linear. It unfolds through questions, comparisons, and the slow accumulation of understanding. This platform is an attempt to support that process—offering simple tools that make exploration a little easier, and perhaps a little more inviting.
        </p>
        <p>
          I hope it serves as a bridge for readers who wish to enter these texts thoughtfully, one word and one insight at a time.
        </p>
      </section>

      <section class="invite" aria-labelledby="share">
        <h2 id="share">
          <a href="mailto:thamizh.words@gmail.com?subject=Tamizh%20Literature%20Search%20—%20Ideas%20and%20Feedback" class="journey-link">Share your ideas and feedback</a>
        </h2>
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
  text-align: center;
}

.journey-link {
  color: var(--primary-color);
  text-decoration: none;
  transition: all 0.3s ease;
}

.journey-link:hover {
  color: var(--primary-dark);
  text-decoration: underline;
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
