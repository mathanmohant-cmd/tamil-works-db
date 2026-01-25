<template>
  <div class="journey-page">
    <div class="container">
      <h1>The Paths Opened by a Few Curious Words</h1>
  
      <section class="intro-section">
        <!-- Introduction
        <p class="intro">
          It started within the Chicago Thamizh Sangam community. A paper presented at the 5th International Conference on Thirukkural offered an early glimpse into how the ideas sown by the Thirukkural continue to shape thought and values even today.
        </p>
        <p class="intro">
          It also awakened a desire to engage more deeply with works such as <em>Tholkappiyam, Thirukkural, Sangam Literature, Silapathikaram,</em> and <em>Kambaramayanam</em>—the foundational texts of Thamizh literary and cultural consciousness.
        </p>
        <p class="intro">
          What might have remained a dormant wish came alive through the தமிழ்ச் சான்றோர்—the scholars, and exemplars whose lifelong work illuminated the path and shaped my understanding.
        </p>
        -->
        <p class="intro">
          When reading the texts, certain words and usages often stand out and spark curiosity—prompting a pause, comparison, and a return to the text with fresh questions.
        </p>
        <p class="intro">
          For example:
        </p>
        <ul class="intro">
          <li><strong>பா, பாய், பாட்டு, பாம்பு</strong> – ideas of spreading and expansion</li>
          <li><strong>கல், கல்வி, கற்பு</strong> – strength, learning, steadiness</li>
          <li><strong>யா, யாமம், யானை, யாணர்</strong> – darkness, the unfamiliar, the new</li>
          <li><strong>எல், எல்லை, எல்லன்</strong> – visibility and boundary</li>
        </ul>
        <p class="intro">
          These are moments of curiosity that many readers encounter while engaging with the texts. Yet following such threads across poems, genres, and commentaries can be difficult without simple ways to search and compare.
        </p>
        <p class="intro">With the help of AI tools and online collaboration, it is now possible to build thoughtful, reader-centered tools that support close engagement with classical literature. Used with care, these technologies can assist—rather than replace—the patient work of reading, comparison, and interpretation.
        </p>
        <p class="intro">Prof. P. Pandiaraja's <a href="http://tamilconcordance.in/">Thamizh Concordance</a> brings Sangam Literature much closer. This attempt is to bring it one more step forward. Hope others will take it further.
        </p>
        <p class="author-name">— T. Mathan Mohan</p>
      <!--
      <p class="closing-reflection">
          <br>Whatever purpose brings you to this platform, I ask that you approach these texts with care and humility.
          <br>These tools are meant to support deeper engagement with the texts, not to reduce them to data points in service of predetermined conclusions.
      </p>
      -->
      </section>
      <!-- Call to Action
      <section class="invite" aria-labelledby="share">
        <h2><em>கற்றது கைமண் அளவு; கல்லாதது உலகளவு</em></h2>
        <h2 id="share">
          <a href="mailto:thamizh.words@gmail.com?subject=Thamizh%20Literature%20Search%20—%20Ideas%20and%20Feedback" class="journey-link">Please share your ideas and feedback</a>
        </h2>
        
      </section>
       -->
    </div>
  </div>
</template>

<script>
export default {
  name: 'OurJourney'
}
</script>

<style scoped>
.journey-page {
  padding: 0rem .25rem;
  background-color: #fafafa;
}

.container {
  max-width: 1000px;
  margin: auto;
  padding: 40px 20px;
}

h1 {
  text-align: left;
  margin-bottom: 0.5rem;
  color: #222;
  font-size: 28px;
}

.author-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary-color);
  margin-top: 0;
  margin-bottom: 2rem;
}

h2 {
  text-align: left;
  margin-top: 3rem;
  margin-bottom: 1.5rem;
  color: var(--primary-color);
  font-size: 24px;
  font-weight: 700;
}

.intro-section {
  margin-bottom: 1rem;
}

.intro {
  font-size: 16px;
  margin-bottom: 1rem;
  line-height: 1.8;
  color: #333;
}

ul.intro {
  padding-left: 2rem;
  margin-left: 0;
}

ul.intro li {
  margin-bottom: 0.5rem;
}

.teachers-section {
  margin-top: 1rem;
}

.mentor-block {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 50px;
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
}

.mentor-block img,
.mentor-block .placeholder-image {
  width: 150px;
  height: 150px;
  min-width: 150px;
  border-radius: 12px;
  object-fit: cover;
}

.placeholder-image {
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-image svg {
  width: 100%;
  height: 100%;
  border-radius: 12px;
}

.mentor-text h3 {
  margin: 0 0 5px 0;
  font-size: 1.3rem;
  color: #222;
  text-align: center
}

.mentor-text p {
  margin: 0 0 1rem 0;
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  text-align: left
}

.mentor-text p:last-of-type {
  margin-bottom: 1;
}

.mentor-text em {
  font-style: italic;
  color: #555;
}

.mentor-text strong {
  font-weight: 600;
  color: #6b2c91;
}

.articles {
  color: #0f4c81;
  text-decoration: none;
  border-bottom: 1px dotted var(--life-pulse);
  font-weight: 600;
}

.articles:hover {
  border-bottom: 1px solid var(--life-pulse);
}


.closing-reflection {
  margin-top: 2rem;
  margin: 1.5rem 2;
  padding: 0rem 1.0rem;
  font-size: 17px;
  line-height: 1.9;
  color: #2d2d2d;
  font-style: italic;
  background: linear-gradient(135deg, #f5f0ff 0%, #fff5f5 100%);
  border-left: 4px solid var(--life-pulse);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(107, 44, 145, 0.1);
  text-align: center;
  font-weight: 500;
}

.tool-section {
  margin-top: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
}

.tool-section p {
  margin: 1rem 0;
  font-size: 16px;
  line-height: 1.8;
  color: #333;
}

.list {
  margin: 1rem 0;
  padding-left: 1.5rem;
  list-style: none;
}

.list li {
  margin: 0.75rem 0;
  font-size: 16px;
  color: #333;
  line-height: 1.7;
}

.resources {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
  
}

.resources h4 {
  font-size: 1.1rem;
  margin: 0 0 10px 0;
  color: #6b2c91;
  font-weight: 600;
  
}

.resources ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.resources li {
  margin: 8px 0;
  font-size: 15px;
  line-height: 1.6;
}

.resources a {
  color: #6b2c91;
  text-decoration: none;
  font-weight: 600;
  font-family: var(--tamil-font), var(--english-font);
  border-bottom: 1px dotted var(--life-pulse);
}

.resources a:hover {
  
  border-bottom: 2px dotted var(--life-pulse);
}

.invite {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  /*border: 2px solid var(--life-pulse);*/
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 3rem;
  text-align: center;
}

.invite h2 {
  margin: 0;
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

@media (max-width: 700px) {
  .mentor-block {
    flex-direction: column;
    text-align: center;
  }

  .mentor-block img,
  .mentor-block .placeholder-image {
    margin: 0 auto 15px auto;
  }

  h1 {
    font-size: 24px;
  }

  h2 {
    font-size: 20px;
  }
}
</style>
