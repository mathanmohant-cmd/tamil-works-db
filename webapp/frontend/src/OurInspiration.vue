<template>
  <div class="inspiration-page">
    <div class="container">
      <h1>Our Inspiration</h1>

      <p class="intro">
        This project is inspired by the dedication of Tamizh scholars, teachers, and enthusiasts
        who have made Tamizh literature accessible to learners across the world.
        Their work sparked our curiosity to explore further, eventually leading to the creation
        of this Tamizh Word Search initiative.
      </p>

      <!-- Prof. Dr. P. Pandiyaraja -->
      <div class="mentor-block">
        <img src="/prof-pandiaraja.jpg" alt="Prof. Dr. P. Pandiyaraja">
        <div class="mentor-text">
          <h3>Prof. Dr. P. Pandiyaraja</h3>
          <p>
            His lifelong work in Tamizh scholarship, especially the creation of the
            <strong>Tamizh Concordance</strong>, shaped much of this project. His meticulous
            research, deep knowledge, and generosity in sharing it have been guiding lights
            for learners everywhere.
          </p>
        </div>
      </div>

      <!-- Ms. Vaidehi Herbert -->
      <div class="mentor-block">
        <div class="placeholder-image">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150">
            <circle cx="75" cy="75" r="75" fill="#e0e0e0"/>
            <circle cx="75" cy="60" r="25" fill="#bdbdbd"/>
            <path d="M 30 120 Q 75 100 120 120" fill="#bdbdbd"/>
          </svg>
        </div>
        <div class="mentor-text">
          <h3>Ms. Vaidehi Herbert</h3>
          <p>
            Her *Introduction to Sangam Literature* courses and the community of learners she nurtures
            opened my door for our deeper engagement with classical Tamizh literature. Her enthusiasm
            and unwavering commitment have made Sangam texts accessible to younger readers and non Tamizh speakers too.
          </p>
        </div>
      </div>

      <!-- Prof. Dr. Ku. Ve. Balasubramanian -->
      <div class="mentor-block">
        <div class="placeholder-image">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150">
            <circle cx="75" cy="75" r="75" fill="#e0e0e0"/>
            <circle cx="75" cy="60" r="25" fill="#bdbdbd"/>
            <path d="M 30 120 Q 75 100 120 120" fill="#bdbdbd"/>
          </svg>
        </div>
        <div class="mentor-text">
          <h3>Prof. Dr. Ku. Ve. Balasubramanian</h3>
          <p>
            Even at the age of 80, he continues to share his vast knowledge through detailed
            teachings on *Silapadhikaram* and *Tholkappiyam*. His 75+ episode Silapadhikaram series
            and 80+ episode Tholkappiyam series in YouTube are treasures that inspire anyone who loves Tamizh.
          </p>
        </div>
      </div>

      <!-- R. Balakrishnan IAS -->
      <div class="mentor-block">
        <div class="placeholder-image">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150">
            <circle cx="75" cy="75" r="75" fill="#e0e0e0"/>
            <circle cx="75" cy="60" r="25" fill="#bdbdbd"/>
            <path d="M 30 120 Q 75 100 120 120" fill="#bdbdbd"/>
          </svg>
        </div>
        <div class="mentor-text">
          <h3>R. Balakrishnan, IAS</h3>
          <p>
            His work in connecting Sangam literature with modern understanding has made classical Tamizh
            closer to today's generation. His ability to distill profound insights from ancient texts
            reflects deep passion, rigor, and scholarship.
          </p>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: 'OurInspiration'
}
</script>

<style scoped>
.inspiration-page {
  padding: 2rem 1rem;
  background-color: #fafafa;
}

.container {
  max-width: 900px;
  margin: auto;
  padding: 40px 20px;
}

h1 {
  text-align: left;
  margin-bottom: 20px;
  color: #222;
  font-size: 28px;
}

h2 {
  text-align: left;
  margin-bottom: 20px;
  color: #222;
  font-size: 24px;
}

.intro {
  font-size: 16px;
  margin-bottom: 40px;
  line-height: 1.8;
  color: #333;
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
  margin: 0 0 10px 0;
  font-size: 1.4rem;
  color: #222;
}

.mentor-text p {
  margin: 0;
  font-size: 16px;
  line-height: 1.8;
  color: #333;
}

.mentor-text em {
  font-style: italic;
  color: #555;
}

.mentor-text strong {
  font-weight: 600;
  color: #6b2c91;
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
}
</style>
