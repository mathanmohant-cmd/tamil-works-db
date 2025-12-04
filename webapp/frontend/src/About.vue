<template>
  <div class="about-page">
    <div class="about-container">
      <h2>About Us</h2>
      <p class="message">
        We are still building this page. Please come back later.
      </p>
      <p class="thanks">
        Thanks for your patience! 🙏
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'About'
}
</script>

<style scoped>
.about-page {
  padding: 3rem 1rem;
  max-width: 800px;
  margin: 0 auto;
  min-height: 50vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.about-container {
  background: #fdfaf6;
  padding: 3rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  text-align: center;
}

.about-container h2 {
  color: #6b2c91;
  font-size: 2rem;
  margin-bottom: 1.5rem;
}

.about-container .message {
  font-size: 1.2rem;
  color: #555;
  margin-bottom: 1rem;
}

.about-container .thanks {
  font-size: 1.1rem;
  color: #777;
  font-style: italic;
}
</style>
