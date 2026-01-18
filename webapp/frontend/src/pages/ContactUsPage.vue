<template>
  <div class="static-page">
    <div class="page-container">
      <h1>Contact Us</h1>

      <section class="content-section">
        <h2>Get in Touch</h2>
        <p>We'd love to hear from you! Whether you have questions, suggestions, feedback, or want to report an issue, please feel free to reach out.</p>
      </section>

      <section class="content-section">
        <h2>Email</h2>
        <p>Send us an email at:</p>
        <div class="contact-info">
          <a href="mailto:thamizh.words@gmail.com" class="email-link">
            📧 thamizh.words@gmail.com
          </a>
        </div>
      </section>

      <section class="content-section">
        <h2>What Can You Contact Us About?</h2>
        <div class="contact-grid">
          <div class="contact-item">
            <h3>🐛 Bug Reports</h3>
            <p>Found something not working correctly? Let us know!</p>
          </div>

          <div class="contact-item">
            <h3>💡 Feature Requests</h3>
            <p>Have an idea for a new feature? We're always looking to improve!</p>
          </div>

          <div class="contact-item">
            <h3>📚 Content Corrections</h3>
            <p>Notice an error in the data? Help us maintain accuracy!</p>
          </div>

          <div class="contact-item">
            <h3>❓ General Questions</h3>
            <p>Have questions about how to use the tool? Ask away!</p>
          </div>

          <div class="contact-item">
            <h3>🤝 Collaboration</h3>
            <p>Interested in partnering or contributing? We'd love to connect!</p>
          </div>

          <div class="contact-item">
            <h3>💬 Feedback</h3>
            <p>Share your experience and help us make this better!</p>
          </div>
        </div>
      </section>

      <section class="content-section">
        <h2>Response Time</h2>
        <p>We aim to respond to all inquiries within 2-3 business days. Please note that this is a community-driven project, and response times may vary depending on the volume of messages.</p>
      </section>

      <section class="content-section">
        <h2>Social Media & Community</h2>
        <p>Stay updated with the latest features and announcements:</p>
        <ul>
          <li>Follow us for updates and Tamil literature insights</li>
          <li>Join discussions about classical Tamil texts</li>
          <li>Connect with other Tamil literature enthusiasts</li>
        </ul>
        <p class="note"><em>Note: Social media channels are coming soon. For now, email is the best way to reach us!</em></p>
      </section>

      <div class="back-link">
        <router-link :to="{ name: 'Home' }">← Back to Home</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// Static Contact Us page
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

.content-section h3 {
  font-size: 1.2rem;
  margin: 0 0 0.5rem 0;
  color: var(--primary-color);
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

.contact-info {
  text-align: center;
  margin: 2rem 0;
}

.email-link {
  display: inline-block;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
  color: white;
  text-decoration: none;
  font-size: 1.2rem;
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
}

.email-link:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4);
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 1.5rem 0;
}

.contact-item {
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
  padding: 1.5rem;
  border-radius: 10px;
  border: 2px solid var(--border-color);
  transition: all 0.3s ease;
}

.contact-item:hover {
  border-color: var(--secondary-color);
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.contact-item p {
  text-align: left;
  margin: 0.5rem 0 0 0;
  font-size: 1rem;
}

.note {
  font-style: italic;
  color: var(--text-secondary);
  font-size: 0.95rem;
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

  .email-link {
    font-size: 1rem;
    padding: 0.75rem 1.5rem;
  }

  .contact-grid {
    grid-template-columns: 1fr;
  }
}
</style>
