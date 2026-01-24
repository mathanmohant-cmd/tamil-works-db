<template>
  <div class="role-selector-overlay">
    <div class="role-selector-modal">
      <h2>Welcome to Thamizh Word Explorer</h2>
      <p class="subtitle">Choose how you'd like to continue</p>

      <div class="options-container">
        <!-- Guest Option -->
        <div class="option-card guest-card">
          <div class="card-icon">👤</div>
          <h3>Continue as Guest</h3>
          <p>Access search and explore Tamil literature</p>
          <button @click="handleGuestAccess" class="btn-guest">
            Continue as Guest
          </button>
        </div>

        <!-- Admin Login Option -->
        <div class="option-card login-card">
          <div class="card-icon">🔑</div>
          <h3>Admin Login</h3>
          <p>Access Browse Works and manage collections</p>

          <form @submit.prevent="handleLogin" class="login-form">
            <div class="form-group">
              <input
                v-model="username"
                type="text"
                placeholder="Username"
                required
                autocomplete="username"
              />
            </div>
            <div class="form-group">
              <input
                v-model="password"
                type="password"
                placeholder="Password"
                required
                autocomplete="current-password"
              />
            </div>
            <div v-if="error" class="error-message">{{ error }}</div>
            <button type="submit" class="btn-login" :disabled="loading">
              {{ loading ? 'Logging in...' : 'Admin Login' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserRole } from '../composables/useUserRole.js'

const { setGuestRole, login } = useUserRole()

const username = ref('')
const password = ref('')
const error = ref(null)
const loading = ref(false)

const handleGuestAccess = () => {
  setGuestRole()
}

const handleLogin = async () => {
  error.value = null
  loading.value = true

  const result = await login(username.value, password.value)

  if (!result.success) {
    error.value = result.error
    loading.value = false
  }
  // If successful, the composable will update the role and the modal will auto-close
}
</script>

<style scoped>
.role-selector-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.role-selector-modal {
  background: white;
  border-radius: 12px;
  padding: 2.5rem;
  max-width: 900px;
  width: 90%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.role-selector-modal h2 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  text-align: center;
  font-size: 1.8rem;
}

.subtitle {
  text-align: center;
  color: #7f8c8d;
  margin: 0 0 2rem 0;
  font-size: 1rem;
}

.options-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.option-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  transition: all 0.2s;
}

.option-card:hover {
  border-color: #4a90e2;
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.15);
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.option-card h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.option-card p {
  color: #7f8c8d;
  margin: 0 0 1.5rem 0;
  font-size: 0.95rem;
}

/* Guest Card */
.guest-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.btn-guest {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 0.9rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  width: 100%;
}

.btn-guest:hover {
  background: #7f8c8d;
}

/* Login Card */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.form-group {
  text-align: left;
}

.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
}

.error-message {
  color: #e74c3c;
  font-size: 0.85rem;
  text-align: center;
  padding: 0.5rem;
  background: #ffe5e5;
  border-radius: 4px;
}

.btn-login {
  background: #4a90e2;
  color: white;
  border: none;
  padding: 0.9rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 0.5rem;
}

.btn-login:hover:not(:disabled) {
  background: #357abd;
}

.btn-login:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .role-selector-modal {
    padding: 1.5rem;
  }

  .options-container {
    grid-template-columns: 1fr;
  }

  .role-selector-modal h2 {
    font-size: 1.5rem;
  }

  .card-icon {
    font-size: 2.5rem;
  }
}
</style>
