<template>
  <div class="home-page">
    <section class="credit-section">
      <div class="credit-text">
        <h2>Tamil Concordance: A Treasure by Prof. P. Pandiaraja</h2>

        <!-- Centered photo below title -->
        <div class="photo-center">
          <img src="/prof-pandiaraja.jpg" alt="Prof. P. Pandiaraja" />
        </div>

        <p>
          This project is deeply indebted to <strong>Professor P. Pandiaraja</strong>, whose creation of the
          <a href="http://tamilconcordance.in/" target="_blank">Tamil Concordance</a> stands as a monumental resource.
          Over more than <strong>five decades</strong>, he has built a searchable treasure of Tamil words across Sangam and later literature,
          <strong>blending his expertise in mathematics and computers with his passion for Tamil</strong>.
        </p>

        <p>
          His dedication, simplicity, and continuous creative contribution to Tamil long after retirement
          is an inspiration for all.
        </p>

        <h3>His Contribution</h3>
        <ul>
          <li><strong>Five decades of dedication:</strong> Meticulous study of Tamil words across Sangam and later literature.</li>
          <li><strong>Books of precision:</strong> His works reflect an insatiable appetite for exactness and nuanced understanding.</li>
          <li><strong>Mathematics meets language:</strong> Introduced statistical and computational methods into Tamil word studies.</li>
          <li><strong>Interdisciplinary bridge:</strong> Blended academic expertise in mathematics, computing, and Tamil culture.</li>
        </ul>

        <h3>Why It Matters</h3>
        <p>
          His work provides researchers with structured concordance, scholars with a foundation for comparative studies, and Tamil speakers everywhere with deeper insights into their language.
        </p>

        <p class="gratitude">
          We extend heartfelt thanks to Prof. P. Pandiaraja for granting permission to use his work. His scholarship is not only a resource but an inspiration, reminding us that Tamil's timeless beauty can be studied with both passion and precision.
        </p>

        <p class="bio-link">
          📖 Read more about his journey in his
          <a href="http://tamilconcordance.in/ennaippaRRi.html" target="_blank">self‑biography</a>.
        </p>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home-page {
  padding: 2rem 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.credit-section {
  background: #fdfaf6;
  padding: 2rem;
  border-radius: 8px;
  margin: 0 auto;
  max-width: 900px;
  line-height: 1.6;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.credit-text h2 {
  color: #6b2c91;
  margin-top: 0;
  text-align: center;
  font-size: 1.8rem;
}

.photo-center {
  display: flex;
  justify-content: center;
  margin: 1.5rem 0;
}

.photo-center img {
  width: 200px;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid #6b2c91;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.credit-text h3 {
  color: #444;
  margin-top: 1.5rem;
  font-size: 1.3rem;
}

.credit-text p {
  margin: 1rem 0;
  color: #333;
}

.credit-text ul {
  margin: 0.5rem 0 1rem 1.5rem;
}

.credit-text li {
  margin-bottom: 0.5rem;
  color: #333;
}

.credit-text .gratitude {
  font-style: italic;
  margin-top: 1.5rem;
  background: #f0e6f6;
  padding: 1rem;
  border-left: 4px solid #6b2c91;
  border-radius: 4px;
}

.credit-text .bio-link {
  margin-top: 2rem;
  text-align: center;
  font-size: 1.1rem;
}

.credit-text .bio-link a {
  color: #6b2c91;
  text-decoration: none;
  font-weight: bold;
}

.credit-text .bio-link a:hover {
  text-decoration: underline;
}

.credit-text a {
  color: #6b2c91;
  font-weight: 600;
}

.credit-text a:hover {
  text-decoration: underline;
}
</style>
