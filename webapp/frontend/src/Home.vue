<template>
  <div class="home-page">
    <article class="tribute-content">
      <header class="tribute-header">
        <h1>Tamizh Concordance: A Treasure by Prof. P. Pandiyaraja</h1>
        <p class="lead">An acknowledgement honoring the scholar whose concordance has shaped this project.</p>
      </header>

      <section class="content">
        <p>This project owes its deepest gratitude to <strong>Prof. P. Pandiyaraja</strong>, whose creation of the
          <a class="concordance" href="http://tamilconcordance.in/" target="_blank" rel="noopener noreferrer">Tamizh Concordance</a>
          stands as a monumental contribution to Tamizh scholarship. Over more than five decades, he has built a priceless repository of Tamizh words drawn from Sangam and post-Sangam literature, blending rigorous mathematical thinking and early computational methods with an unwavering love for Tamizh.</p>

        <p>His work offers researchers a robust and structured concordance, opening up immense opportunities for etymological analysis of Tamizh words, their usage, and the development of their meanings. For Tamizh aficionados, this is a gift of easy access to classical Tamizh, furthering a deeper appreciation of the language's richness and depth.</p>

        <blockquote class="tribute-quote">
          "This search tool is merely an extension of his lifelong labor. When I reached out to him, he warmly shared his wishes to see such a tool built. It is my immense pleasure and honor to help fulfill that vision."
        </blockquote>

        <p>I extend my heartfelt thanks to Prof. P. Pandiyaraja for granting permission to build upon his work. <strong>His scholarship is not only a resource but an enduring inspiration.</strong></p>
      </section>
    </article>
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
  max-width: 900px;
  margin: 0 auto;
}

.tribute-content {
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(11, 33, 65, 0.08);
  padding: 32px;
  line-height: 1.8;
  color: #122233;
  font-size: 16px;
}

.tribute-header {
  margin-bottom: 18px;
}

.tribute-header h1 {
  margin: 0;
  font-size: 26px;
  color: #07203a;
  font-weight: 700;
}

.lead {
  margin: 6px 0 0;
  color: #6b7280;
  font-size: 16px;
}

.content {
  margin-top: 12px;
}

.section-title {
  font-weight: 700;
  margin-top: 18px;
  margin-bottom: 6px;
  color: #0b3b5c;
  font-size: 1.5rem;
}

.content p {
  margin: 1rem 0;
  color: #122233;
}

.concordance {
  color: #0f4c81;
  text-decoration: none;
  border-bottom: 1px dotted rgba(11, 76, 129, 0.25);
  font-weight: 600;
}

.concordance:hover {
  border-bottom: 1px solid #0f4c81;
}

.tribute-quote {
  margin: 18px 0;
  padding: 14px 18px;
  border-left: 4px solid #0f4c81;
  background: #fbfdff;
  border-radius: 8px;
  color: #0b3b5c;
  font-style: italic;
  font-size: 16px;
}

@media (max-width: 768px) {
  .tribute-content {
    padding: 20px;
  }

  .tribute-header h1 {
    font-size: 20px;
  }
}
</style>
