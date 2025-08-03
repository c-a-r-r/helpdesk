<template>
  <div class="auth-callback-container">
    <div class="auth-callback-card">
      <h2>Processing Login...</h2>
      <div class="loader" v-if="loading"></div>
      <div v-if="error" class="error-message">
        <h3>Login Error</h3>
        <p>{{ errorMessage }}</p>
        <button @click="returnToLogin" class="return-btn">Return to Login</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(true)
const error = ref(false)
const errorMessage = ref('')

onMounted(() => {
  processCallback()
})

const processCallback = async () => {
  // Get the query parameters
  const urlParams = new URLSearchParams(window.location.search)
  
  // Check if there's an error
  if (urlParams.has('error')) {
    error.value = true
    errorMessage.value = `Authentication error: ${urlParams.get('error')}`
    if (urlParams.has('details')) {
      errorMessage.value += ` - ${urlParams.get('details')}`
    }
    loading.value = false
    return
  }

  // Check if there's a token and user data
  if (urlParams.has('token') && urlParams.has('user')) {
    try {
      // Store the token and user data
      const token = urlParams.get('token')
      const userData = JSON.parse(decodeURIComponent(urlParams.get('user')))
      
      sessionStorage.setItem('userToken', token)
      sessionStorage.setItem('userClaims', JSON.stringify(userData))
      
      // Redirect to dashboard
      router.push('/dashboard')
    } catch (err) {
      error.value = true
      errorMessage.value = `Error processing authentication: ${err.message}`
      loading.value = false
    }
  } else {
    error.value = true
    errorMessage.value = 'Missing authentication data in callback'
    loading.value = false
  }
}

const returnToLogin = () => {
  router.push('/')
}
</script>

<style scoped>
.auth-callback-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.auth-callback-card {
  width: 90%;
  max-width: 500px;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background-color: white;
  text-align: center;
}

.loader {
  margin: 20px auto;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #e74c3c;
  margin-top: 20px;
}

.return-btn {
  background-color: #3498db;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  margin-top: 20px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.return-btn:hover {
  background-color: #2980b9;
}
</style>
