<template>
  <div class="help-page">
    <!-- Breadcrumb -->
    <nav class="breadcrumb">
      <router-link :to="{ name: 'Help' }">Help</router-link>
      <span class="separator">›</span>
      <span>Understanding This Tool</span>
    </nav>

    <!-- Page Header -->
    <header class="page-header">
      <h1>Understanding This Tool</h1>
    </header>

    <!-- Table of Contents -->
    <nav class="table-of-contents">
      <h3>Contents</h3>
      <ul>
        <li><a href="#how-search-works">How Does This Tool Search Across Literary Works?</a></li>
        <li><a href="#what-is-concordance">What is a Concordance?</a></li>
        <li><a href="#dictionary-difference">How is Concordance Different from a Dictionary?</a></li>
        <li><a href="#why-important">Why is Concordance Important?</a></li>
        <li><a href="#how-to-use">How to Use This Tool?</a></li>
        <li><a href="#other-features">What other Features are possible?</a></li>
        <li><a href="#final-thoughts">Final Thoughts</a></li>
      </ul>
    </nav>

    <!-- Content Sections -->
    <section id="how-search-works" class="content-section">
      <h2>How Does This Tool Search Across Literary Works?</h2>
      <p>This tool is built like a powerful database that <strong>breaks down every verse</strong> into individual words and remembers where each word came from.</p>

      <div class="process-section">
        <h3>Here's What Happens Behind the Scenes:</h3>

        <div class="process-step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h4>Data Preparation:</h4>
            <p><strong>Acknowledgment:</strong> This searchable concordance is built upon the comprehensive data compiled by <strong>Prof. Dr. P. Pandiyaraja</strong> and available at <a href="http://tamilconcordance.in/" target="_blank" rel="noopener noreferrer" class="external-link">tamilconcordance.in</a>. His meticulous work in creating concordance files for Tamil literary works forms the foundation of this database.</p>
            <p>To preserve the integrity of his structure and methodology:</p>
            <ul>
              <li><strong>Sections</strong> of each work are faithfully captured</li>
              <li><strong>Verses</strong> within each section are clearly marked</li>
              <li>Each verse is broken into constituent <strong>lines</strong></li>
              <li>Each line is segmented into <strong>words</strong> following his concordance</li>
              <li>Every word's <strong>position and context</strong> is stored in the database</li>
              <li>Works are grouped in to <strong>collections</strong> for targeted search</li>
            </ul>

            <p class="segmentation-link">
              To understand how Tamil words are segmented — and why segmentation is essential for accurate search, concordance, and interpretation — see
              <router-link :to="{ name: 'WordSegmentation' }" class="tab-link">Word Segmentation Principles →</router-link>
            </p>
          </div>
        </div>

        <div class="process-step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h4>When You Search:</h4>
            <ul>
              <li>You type a Tamil word (like "அறம்")</li>
              <li>The tool instantly searches through <strong>millions of stored words</strong></li>
              <li>It finds every match across all literary works</li>
              <li>It shows you the complete verse and context for each occurrence</li>
            </ul>
          </div>
        </div>

        <div class="process-step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h4>Smart Features:</h4>
            <ul>
              <li><strong>Exact Match:</strong> Find only "அறம்" (not "அறமது" or "அறங்கள்")</li>
              <li><strong>Partial Match:</strong> Find all words containing "அற" (including அறம், அறன், அறிவு, etc.)</li>
              <li><strong>Filter by Work:</strong> Search only in Thirukkural or only in Sangam literature</li>
              <li><strong>Sort by Collection:</strong> See results organized by the chronological order of Tamil literature</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="database-info">
        <h3>What's Inside the Database?</h3>
        <p><strong>The database currently includes works from selected collections:</strong></p>
        <p>Please click on the <strong>Search Box</strong> to see the complete list of works available for search</p>
        <p class="note"><em>Note: The collection continues to grow as more literary works are added to the database.</em></p>
      </div>
    </section>

    <section id="what-is-concordance" class="content-section">
      <h2>What is a Concordance?</h2>
      <p>Think of a concordance as a <strong>super-powered search engine for books</strong>.</p>

      <p>Instead of just telling you what a word means (like a dictionary does), a concordance shows you <strong>every single place that word appears</strong> in a collection of books, along with the full sentence or verse where it's used.</p>

      <div class="example-box">
        <h3>Simple Example:</h3>
        <div class="comparison">
          <div class="comparison-item">
            <strong>Dictionary:</strong>
            <p>"அறம்" means virtue, righteousness, duty</p>
          </div>
          <div class="comparison-item">
            <strong>Concordance:</strong>
            <p>Shows you all the places where "அறம்" appears in Tamil literature, with the complete line and context</p>
          </div>
        </div>
      </div>
    </section>

    <section id="dictionary-difference" class="content-section">
      <h2>How is Concordance Different from a Dictionary?</h2>
      <p>Great question! Here's the key difference:</p>

      <div class="comparison-table">
        <div class="table-row header-row">
          <div class="table-cell">📖 Dictionary</div>
          <div class="table-cell">🔍 Concordance (This Tool)</div>
        </div>
        <div class="table-row">
          <div class="table-cell"><span class="icon">📖</span> Tells you what a word <strong>means</strong></div>
          <div class="table-cell"><span class="icon">🔍</span> Shows you how a word is <strong>actually used</strong></div>
        </div>
        <div class="table-row">
          <div class="table-cell"><span class="icon">📖</span> Gives one or two example sentences</div>
          <div class="table-cell"><span class="icon">🔍</span> Shows <strong>every occurrence</strong> across all literature</div>
        </div>
        <div class="table-row">
          <div class="table-cell"><span class="icon">📖</span> Definition is the same for everyone</div>
          <div class="table-cell"><span class="icon">🔍</span> You see how <strong>different authors</strong> used the same word</div>
        </div>
        <div class="table-row">
          <div class="table-cell"><span class="icon">📖</span> Useful for learning vocabulary</div>
          <div class="table-cell"><span class="icon">🔍</span> Useful for understanding <strong>context, usage patterns, and deeper meanings</strong></div>
        </div>
      </div>

      <div class="example-box">
        <h3>Real-World Example</h3>
        <p>Let's say you search for the word <strong>"காதல்" (love)</strong>:</p>
      </div>

      <div class="example-content">
        <h4>📖 What a dictionary tells you:</h4>
        <div class="dictionary-result">
          <p class="definition">காதல் = Love, affection</p>
        </div>

        <h4>🔍 What THIS tool tells you:</h4>
        <div class="concordance-result">
          <ul>
            <li><strong>How many different works</strong> காதல் appears in</li>
            <li><strong>How many verses</strong> across Sangam literature, Thirukkural, and devotional texts காதல் appears</li>
            <li>Location reference and option to <strong>Export</strong> for further analysis.</li>
            <li>Gives a sense of the context - In Sangam poetry, it appears in nature imagery and love poems. In devotional literature, it describes divine love for God</li>
          </ul>
        </div>

        <div class="key-difference">
          <strong>The difference?</strong> You're not just learning what the word means — you're learning how great Tamil poets and saints actually used it across 2,000 years of literature!
        </div>
      </div>
    </section>

    <section id="why-important" class="content-section">
      <h2>Why is Concordance Important?</h2>

      <div class="importance-grid">
        <div class="importance-item">
          <div class="importance-number">1</div>
          <h3>See Words in Real Context</h3>
          <p>Words change meaning based on context. By seeing all the places a word appears, you understand its <strong>full range of meanings</strong> and how ancient authors actually used it.</p>
        </div>

        <div class="importance-item">
          <div class="importance-number">2</div>
          <h3>Discover Connections Between Works</h3>
          <p>See how the same word or concept appears across different time periods and literary traditions. For example:</p>
          <ul>
            <li>How did Sangam poets use a word?</li>
            <li>How did Thiruvalluvar use the same word years later?</li>
            <li>How did devotional poets use it differently?</li>
          </ul>
        </div>

        <div class="importance-item">
          <div class="importance-number">3</div>
          <h3>Research and Analysis</h3>
          <p>For students writing essays or researchers studying Tamil literature:</p>
          <ul>
            <li>Find all verses with a specific word</li>
            <li>Compare how different authors developed the word usage</li>
            <li>Track the evolution of word usage over time</li>
          </ul>
        </div>

        <div class="importance-item">
          <div class="importance-number">4</div>
          <h3>Deeper Literary Appreciation</h3>
          <p>Instead of reading one work in isolation, you can see the <strong>conversation between authors across centuries</strong>. Tamil literature is like a long conversation — concordance lets you see all the threads.</p>
        </div>
      </div>
    </section>

    <section id="how-to-use" class="content-section">
      <h2>How to Use This Tool?</h2>

      <div class="student-uses">
        <div class="importance-item">
          <h3>For Tamil Language Learning:</h3>
          <ul>
            <li>See how words are actually used in sentences</li>
            <li>Learn synonyms by finding different words used in similar contexts</li>
            <li>Build vocabulary by exploring word families</li>
          </ul>
        </div>

        <div class="importance-item">
          <h3>For Research Projects:</h3>
          <ul>
            <li>Gather all references to a specific topic</li>
            <li>Analyze patterns across different works</li>
            <li>Support your arguments with textual evidence</li>
          </ul>
        </div>

        <div class="importance-item">
          <h3>For Personal Exploration:</h3>
          <ul>
            <li>Discover beautiful verses you've never read</li>
            <li>Follow your curiosity about specific words or concepts</li>
            <li>Develop a deeper connection to Tamil heritage</li>
          </ul>
        </div>
      </div>
      <p><em>* Rigorous care has been taken to preserve the accuracy of the data presented on tamilconcordance.in. However, this tool is designed for quick and convenient access, and it should not be considered a substitute for individual verification when used for academic or scholarly work. *</em>
      </p>
    </section>

    <section id="other-features" class="content-section">
      <h2>What other Features are possible?</h2>
      <p>With collaboration from experts across multiple domains, there are exciting possibilities to explore together.</p>

      <div class="features-grid">
        <div class="feature-item">
          <h3>1. Word Root Analysis</h3>
          <ul>
            <li>Show all forms of a word (அறம், அறன், அறமது, அறங்கள்)</li>
            <li>Understand how Tamil grammar changes words</li>
          </ul>
        </div>

        <div class="feature-item">
          <h3>2. Translation Layer</h3>
          <ul>
            <li>Side-by-side Tamil and English translations</li>
            <li>Help non-Tamil speakers explore the literature</li>
          </ul>
        </div>

        <div class="feature-item">
          <h3>3. Thematic Search</h3>
          <ul>
            <li>Search by concept (not just words): "all verses about rain," "all verses about friendship"</li>
            <li>Group related words together automatically</li>
          </ul>
        </div>

        <div class="feature-item">
          <h3>4. Comparative Analysis</h3>
          <ul>
            <li>Compare how two different authors used the same word</li>
            <li>Visualize word usage patterns over time</li>
            <li>See which words appear together frequently</li>
          </ul>
        </div>

        <div class="feature-item">
          <h3>5. Audio Pronunciation</h3>
          <ul>
            <li>Hear classical Tamil pronounced correctly</li>
            <li>Learn proper meter and rhythm for verses</li>
          </ul>
        </div>

        <div class="feature-item">
          <h3>6. Commentary Integration</h3>
          <ul>
            <li>Show traditional scholarly commentaries alongside verses</li>
            <li>Link to explanations by famous scholars</li>
          </ul>
        </div>

        <div class="feature-item">
          <h3>7. Personal Study Tools</h3>
          <ul>
            <li>Save favorite verses</li>
            <li>Create custom collections for study</li>
            <li>Add personal notes and annotations</li>
          </ul>
        </div>

        <div class="feature-item">
          <h3>8. Advanced Filters</h3>
          <ul>
            <li>Search by time period (Sangam era vs. Medieval)</li>
            <li>Search by literary genre (love poetry vs. ethical verses)</li>
            <li>Search by meter/poetic form</li>
          </ul>
        </div>

        <div class="feature-item">
          <h3>9. Visualization Features</h3>
          <ul>
            <li>Word frequency charts</li>
            <li>Networks showing which words appear together</li>
            <li>Timeline of how word usage evolved</li>
          </ul>
        </div>

        <div class="feature-item">
          <h3>10. Educational Features</h3>
          <ul>
            <li>Quiz yourself on word meanings from context</li>
            <li>Interactive lessons on Tamil literary history</li>
            <li>Guided tours through related verses</li>
          </ul>
        </div>
      </div>
    </section>

    <section id="final-thoughts" class="content-section">
      <h2>Final Thoughts</h2>
      <div class="highlight-box">
        <p class="big-text"><strong>A dictionary tells you what words mean.</strong></p>
        <p class="big-text"><strong>A concordance shows you how words LIVE in the real world of literature.</strong></p>
      </div>

      <p>This tool is your gateway to exploring 2,000+ years of Tamil literary genius. Every search is an adventure — you never know what beautiful verse or profound insight you'll discover next.</p>
    </section>

    <footer class="page-footer">
      <p>If you have questions about how to use this tool or suggestions for new features, <a href="mailto:thamizh.words@gmail.com?subject=Thamizh%20Literature%20Search%20—%20Ideas%20and%20Feedback">we'd love to hear from you</a>. This is a living project designed to help everyone — from students to scholars — explore the beauty of Tamil literature.</p>
      <p><strong>Happy searching!</strong></p>
    </footer>
  </div>
</template>

<script setup>
import { useAnchorScroll } from '../composables/useAnchorScroll'

// Enable smooth scrolling for anchor links
useAnchorScroll()
</script>

<style scoped>
/* Base page styles */
.help-page {
  padding: 2rem 1rem;
  max-width: 1000px;
  margin: 0 auto;
  background: var(--surface);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

.content-section h2 {
  scroll-margin-top: 80px;
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
  color: var(--text-secondary);
}

.breadcrumb a {
  color: var(--secondary-color);
  text-decoration: none;
  transition: color 0.2s ease;
}

.breadcrumb a:hover {
  color: var(--primary-color);
  text-decoration: underline;
}

.breadcrumb .separator {
  color: var(--text-secondary);
}

/* Page Header */
.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--primary-color);
}

.page-header h1 {
  font-size: 2rem;
  margin: 0 0 0.5rem 0;
  color: var(--primary-color);
  font-weight: 700;
}

.subtitle {
  margin: 0.5rem 0;
  color: var(--text-secondary);
  font-size: 1.1rem;
  font-style: italic;
}

/* Table of Contents */
.table-of-contents {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border: 2px solid var(--border-color);
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.table-of-contents h3 {
  margin: 0 0 1rem 0;
  color: var(--primary-color);
  font-size: 1.2rem;
  font-weight: 600;
}

.table-of-contents ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.table-of-contents li {
  margin: 0.5rem 0;
}

.table-of-contents a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  border-bottom: 1px dotted rgba(25, 118, 210, 0.3);
}

.table-of-contents a:hover {
  color: var(--primary-color);
  border-bottom: 1px solid var(--primary-color);
}

/* Content Sections */
.content-section {
  padding: 2rem 1.5rem;
  line-height: 1.7;
  border-bottom: 1px solid var(--border-color);
}

.content-section:last-of-type {
  border-bottom: none;
}

.content-section h2 {
  font-size: 1.6rem;
  color: var(--primary-color);
  margin: 0 0 1.5rem 0;
  font-weight: 700;
  border-left: 4px solid var(--primary-color);
  padding-left: 1rem;
}

.content-section h3 {
  font-size: 1.2rem;
  color: var(--secondary-color);
  margin: 1.5rem 0 1rem;
  font-weight: 600;
}

.content-section p {
  margin: 1rem 0;
  color: var(--text-primary);
  font-size: 1.05rem;
  text-align: justify;
}

/* Process Section */
.process-section {
  margin: 1rem 0;
}

.process-step {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
  background: white;
  padding: 1rem 1.25rem;
  border-radius: 10px;
  border: 2px solid var(--border-color);
}

.step-number {
  flex-shrink: 0;
  width: 50px;
  height: 50px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.5rem;
  box-shadow: 0 2px 6px rgba(211, 47, 47, 0.3);
}

.step-content {
  flex: 1;
}

.step-content h4 {
  margin: 0 0 0.75rem 0;
  color: var(--primary-color);
  font-size: 1.15rem;
}

.step-content ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.step-content li {
  margin: 0.5rem 0;
}

.segmentation-link {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border-left: 3px solid var(--primary-color);
  border-radius: 6px;
  font-size: 1rem;
}

.external-link,
.tab-link {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 2px dotted rgba(25, 118, 210, 0.3);
  transition: all 0.2s ease;
}

.external-link:hover,
.tab-link:hover {
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

/* Database Info */
.database-info {
  padding: 1.5rem;
  border-radius: 10px;
  margin: 1.5rem 0;
}

.database-info h3 {
  margin: 0 0 1rem 0;
}

.note {
  font-style: italic;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

/* Example Box */
.example-box {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border: 2px solid var(--secondary-color);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin: 1rem 0;
}

/* Comparison */
.comparison {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.comparison-item {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  border: 2px solid var(--border-color);
}

.comparison-item strong {
  color: var(--primary-color);
  display: block;
  margin-bottom: 0.5rem;
}

/* Comparison Table */
.comparison-table {
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  margin: 1rem 0;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}

.header-row {
  background: linear-gradient(135deg, var(--primary-color) 0%, #c62828 100%);
  color: white;
  font-weight: 700;
}

.table-cell {
  padding: 0.6rem 1rem;
  border-bottom: 1px solid var(--border-color);
  line-height: 1.5;
  font-size: 1.0rem;
}

.table-row:last-child .table-cell {
  border-bottom: none;
}

.table-row:not(.header-row):nth-child(even) {
  background: #f9f9f9;
}

.table-cell .icon {
  display: inline-block;
  margin-right: 0.5rem;
  font-size: 1.2rem;
}

/* Example Content */
.example-content {
  margin-top: 1rem;
}

.example-content h4 {
  color: var(--primary-color);
  margin: 1.5rem 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.example-content h4:first-child {
  margin-top: 0.5rem;
}

.dictionary-result,
.concordance-result {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin: 0 0 1rem 0;
  border: 2px solid var(--border-color);
  font-size: 1.0rem;
}

.definition {
  font-style: italic;
  color: var(--text-secondary);
  padding: 0.5rem 1rem;
  background: #f5f5f5;
  border-left: 3px solid var(--secondary-color);
}

.concordance-result ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.concordance-result li {
  margin: 0.5rem 0;
  color: var(--text-primary);
}

.key-difference {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-top: 1rem;
  border-left: 4px solid #ff9800;
  font-size: 1.05rem;
}

/* Importance Grid */
.importance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.importance-item {
  background: white;
  padding: 1rem 1.25rem;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  position: relative;
  padding-top: 2.5rem;
}

.importance-number {
  position: absolute;
  top: -15px;
  left: 20px;
  background: var(--primary-color);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
  box-shadow: 0 2px 6px rgba(211, 47, 47, 0.3);
}

.importance-item h3 {
  color: var(--secondary-color);
  margin: 0 0 0.75rem 0;
  font-size: 1.15rem;
}

.importance-item p,
.importance-item ul {
  margin: 0.75rem 0;
  font-size: 1rem;
}

.importance-item ul {
  padding-left: 1.5rem;
}

.importance-item li {
  margin: 0.5rem 0;
}

/* Student Uses */
.student-uses {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

/* Features Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.feature-item {
  background: white;
  padding: 1rem 1.25rem;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.feature-item:hover {
  border-color: var(--primary-color);
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(211, 47, 47, 0.15);
}

.feature-item h3 {
  color: var(--primary-color);
  margin: 0 0 0.75rem 0;
  font-size: 1.1rem;
}

.feature-item ul {
  margin: 0;
  padding-left: 1.5rem;
}

.feature-item li {
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

/* Highlight Box */
.highlight-box {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  text-align: center;
  margin: 1rem 0;
  border: 2px solid var(--primary-color);
}

.big-text {
  font-size: 1.2rem;
  margin: 0.75rem 0;
  color: var(--primary-color);
}

/* Footer */
.page-footer {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 2px solid var(--border-color);
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.page-footer p {
  margin: 0.75rem 0;
}

.page-footer a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px dotted rgba(25, 118, 210, 0.25);
}

.page-footer a:hover {
  border-bottom: 1px solid var(--secondary-color);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .help-page {
    padding: 1rem 0.5rem;
  }

  .content-section {
    padding: 1.5rem 1rem;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .content-section h2 {
    font-size: 1.3rem;
  }

  .content-section p,
  .content-section li {
    font-size: 1.05rem;
    line-height: 1.6;
  }

  .comparison {
    grid-template-columns: 1fr;
  }

  .table-row {
    grid-template-columns: 1fr;
  }

  .table-cell {
    padding: 0.6rem 0.75rem;
    font-size: 0.95rem;
  }

  .importance-grid,
  .features-grid,
  .student-uses {
    grid-template-columns: 1fr;
  }

  .process-step {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .step-content {
    text-align: left;
  }

  .step-content p,
  .step-content li {
    font-size: 1.05rem;
  }
}
</style>
