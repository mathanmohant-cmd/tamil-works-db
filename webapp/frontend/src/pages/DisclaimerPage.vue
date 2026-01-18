<template>
  <div class="static-page">
    <div class="page-container">
      <h1>Disclaimer</h1>

      <section class="content-section">
        <h2>General Disclaimer</h2>
        <p>The information provided by Thamizh Word Explorer ("we," "us," or "our") on this website is for general informational and educational purposes only. All information on the site is provided in good faith; however, we make no representation or warranty of any kind, express or implied, regarding the accuracy, adequacy, validity, reliability, availability, or completeness of any information on the site.</p>
      </section>

      <section class="content-section">
        <h2>Data Source & Accuracy</h2>
        <p>This tool is built upon the concordance data compiled by <strong>Prof. Dr. P. Pandiyaraja</strong>, available at <a href="http://tamilconcordance.in" target="_blank" rel="noopener noreferrer">tamilconcordance.in</a>. While rigorous care has been taken to preserve the accuracy and integrity of this data:</p>
        <ul>
          <li>We do not guarantee the absolute accuracy, completeness, or reliability of the information presented</li>
          <li>This tool is designed for quick and convenient access to Tamil literary texts</li>
          <li>For academic research, scholarly work, or official citations, we strongly recommend verifying information against original published sources</li>
          <li>Users should consult authoritative editions and expert scholars for critical interpretations</li>
        </ul>
      </section>

      <section class="content-section">
        <h2>Educational Purpose Only</h2>
        <p>This website and its content are intended solely for educational and research purposes. They should not be used as:</p>
        <ul>
          <li>Authoritative source for legal, religious, or official purposes</li>
          <li>Substitute for professional scholarly analysis</li>
          <li>Primary source for academic citations without independent verification</li>
          <li>Definitive interpretation of classical Tamil texts</li>
        </ul>
      </section>

      <section class="content-section">
        <h2>No Professional Advice</h2>
        <p>The information on this website does not constitute professional advice of any kind (literary, linguistic, historical, or otherwise). Users should seek guidance from qualified experts for specific scholarly or professional purposes.</p>
      </section>

      <section class="content-section">
        <h2>External Links</h2>
        <p>This website may contain links to external websites that are not provided or maintained by us. We do not guarantee the accuracy, relevance, timeliness, or completeness of any information on these external websites.</p>
      </section>

      <section class="content-section">
        <h2>Changes and Updates</h2>
        <p>We reserve the right to modify, update, or remove content from this website at any time without prior notice. The database is continuously evolving as:</p>
        <ul>
          <li>New literary works are added</li>
          <li>Corrections and improvements are made</li>
          <li>Features and functionality are enhanced</li>
          <li>Data accuracy is improved based on user feedback</li>
        </ul>
      </section>

      <section class="content-section">
        <h2>Use at Your Own Risk</h2>
        <p>Your use of this website and reliance on any information provided is solely at your own risk. We shall not be liable for any loss or damage arising from:</p>
        <ul>
          <li>Use or reliance on information from this website</li>
          <li>Inability to access the website or any of its features</li>
          <li>Errors, omissions, or inaccuracies in the content</li>
          <li>Any decision made based on information from this tool</li>
        </ul>
      </section>

      <section class="content-section">
        <h2>Copyright and Intellectual Property</h2>
        <p>The original concordance work is the intellectual property of Prof. Dr. P. Pandiyaraja. The classical Tamil literary texts themselves are in the public domain as works of ancient literature. This website's interface, design, and specific compilation are provided for non-commercial educational use.</p>
      </section>

      <section class="content-section">
        <h2>Technical Limitations</h2>
        <p>While we strive to maintain the highest standards:</p>
        <ul>
          <li>Technical issues, bugs, or errors may occasionally occur</li>
          <li>Search functionality may not capture all edge cases or linguistic variations</li>
          <li>The website's availability is not guaranteed at all times</li>
          <li>Performance may vary based on user's device and internet connection</li>
        </ul>
      </section>

      <section class="content-section">
        <h2>Feedback and Corrections</h2>
        <p>We welcome feedback and corrections from users. If you identify errors or have suggestions for improvement, please <router-link :to="{ name: 'ContactUs' }">contact us</router-link>. However, we cannot guarantee that all suggestions will be implemented or that all reported issues will be addressed.</p>
      </section>

      <section class="content-section">
        <h2>Agreement</h2>
        <p>By using this website, you acknowledge that you have read, understood, and agree to be bound by this disclaimer. If you do not agree with any part of this disclaimer, please discontinue use of the website.</p>
      </section>

      <div class="last-updated">
        <p><em>Last Updated: January 2026</em></p>
      </div>

      <div class="back-link">
        <router-link :to="{ name: 'Home' }">← Back to Home</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// Static Disclaimer page
</script>

<style scoped>
.static-page {
  padding: 2rem 1rem;
  max-width: 900px;
  margin: 0 auto;
}

.page-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin: 0 0 2rem 0;
  border-bottom: 3px solid var(--primary-color);
  padding-bottom: 1rem;
}

.content-section {
  margin: 2rem 0;
}

.content-section h2 {
  font-size: 1.6rem;
  color: var(--secondary-color);
  margin: 0 0 1rem 0;
  font-weight: 600;
}

.content-section p {
  line-height: 1.7;
  color: var(--text-primary);
  margin: 1rem 0;
  font-size: 1.05rem;
  text-align: justify;
}

.content-section ul {
  margin: 1rem 0;
  padding-left: 2rem;
}

.content-section li {
  margin: 0.75rem 0;
  line-height: 1.6;
  color: var(--text-primary);
}

.content-section a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px dotted rgba(25, 118, 210, 0.3);
}

.content-section a:hover {
  border-bottom: 1px solid var(--secondary-color);
}

.last-updated {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
  text-align: center;
}

.last-updated p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
}

.back-link {
  margin-top: 3rem;
  text-align: center;
}

.back-link a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  padding: 0.75rem 1.5rem;
  border: 2px solid var(--secondary-color);
  border-radius: 6px;
  display: inline-block;
  transition: all 0.3s ease;
}

.back-link a:hover {
  background: var(--secondary-color);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(25, 118, 210, 0.2);
}

@media (max-width: 768px) {
  .static-page {
    padding: 1rem 0.5rem;
  }

  .page-container {
    padding: 1.5rem;
  }

  h1 {
    font-size: 2rem;
  }

  .content-section h2 {
    font-size: 1.3rem;
  }

  .content-section p,
  .content-section li {
    font-size: 1rem;
  }
}
</style>
