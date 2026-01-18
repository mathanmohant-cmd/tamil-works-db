<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-links">
        <router-link :to="{ name: 'AboutUs' }" class="footer-link">About Us</router-link>
        <span class="separator">|</span>
        <router-link :to="{ name: 'ContactUs' }" class="footer-link">Contact Us</router-link>
        <span class="separator">|</span>
        <router-link :to="{ name: 'Disclaimer' }" class="footer-link">Disclaimer</router-link>
      </div>
      <div class="footer-copyright">
        <p>&copy; 2026 Thamizh Word Explorer. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
// Simple footer component - no state needed
</script>

<style scoped>
.app-footer {
  background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
  color: white;
  padding: 2rem 1rem;
  margin-top: auto;
  border-top: 3px solid var(--primary-color);
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.footer-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.footer-link:hover {
  color: #ffd700;
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.separator {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 300;
}

.footer-copyright {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin-top: 1rem;
}

.footer-copyright p {
  margin: 0;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .app-footer {
    padding: 1.5rem 1rem;
  }

  .footer-links {
    flex-direction: column;
    gap: 0.5rem;
  }

  .separator {
    display: none;
  }

  .footer-link {
    padding: 0.75rem 1.5rem;
    width: 100%;
    max-width: 300px;
  }

  .footer-copyright {
    font-size: 0.85rem;
  }
}
</style>
