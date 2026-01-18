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
  padding: 1rem 0.5rem;
  margin-top: auto;
  border-top: 2px solid var(--primary-color);
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
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.footer-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  padding: 0.25rem 0.75rem;
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
  font-size: 0.85rem;
}

.footer-copyright {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.75rem;
  margin-top: 0.5rem;
}

.footer-copyright p {
  margin: 0;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .app-footer {
    padding: 0.250rem 0.25rem;
  }

.footer-links {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0;
  width: 100%;
  flex-wrap: nowrap;
}

  .separator {
    display: none;
  }

  .footer-link {
    padding: 0.25rem .25rem;
    width: 100%;
    max-width: 300px;
    font-size: 0.7rem;
  }

  .footer-copyright {
    font-size: 0.7rem;
  }
}
</style>
