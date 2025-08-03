<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-section">
        <h1>Helpdesk CRM</h1>
        <p>Sign in to your account</p>
      </div>
      
      <div class="login-content">
        <div v-if="!claims && !loading">
          <button @click="login" class="login-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
              <polyline points="10,17 15,12 10,7"></polyline>
              <line x1="15" y1="12" x2="3" y2="12"></line>
            </svg>
            Login with JumpCloud
          </button>
        </div>
        
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Authenticating...</p>
        </div>
        
        <div v-if="claims" class="success-state">
          <div class="success-icon">✅</div>
          <p>Welcome {{ getUserDisplayName() }}!</p>
          <p class="redirect-text">Redirecting to dashboard...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const claims = ref(null)
const loading = ref(false)

const login = () => {
  loading.value = true
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  window.location.href = `${apiBaseUrl}/login`
}

const checkAuthStatus = async () => {
  try {
    // Check if we have user claims in session storage (from backend redirect)
    const storedClaims = sessionStorage.getItem('userClaims')
    if (storedClaims) {
      claims.value = JSON.parse(storedClaims)
      // Redirect to dashboard after showing success message
      setTimeout(() => {
        router.push('/dashboard')
      }, 2000)
      return
    }

    // Check URL parameters for auth callback
    const urlParams = new URLSearchParams(window.location.search)
    const token = urlParams.get('token')
    const userInfo = urlParams.get('user')
    
    if (token && userInfo) {
      // Store authentication data
      localStorage.setItem('userToken', token)
      const userClaims = JSON.parse(decodeURIComponent(userInfo))
      sessionStorage.setItem('userClaims', JSON.stringify(userClaims))
      claims.value = userClaims
      
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
      
      // Redirect to dashboard
      setTimeout(() => {
        router.push('/dashboard')
      }, 2000)
    }
  } catch (error) {
    console.error('Auth check failed:', error)
    loading.value = false
  }
}

const getUserDisplayName = () => {
  if (!claims.value) return 'User'
  
  // Try different ways to get the user's name from JumpCloud claims
  let userName = ''
  
  if (claims.value.name) {
    userName = Array.isArray(claims.value.name) ? claims.value.name[0] : claims.value.name
  } else if (claims.value.given_name && claims.value.family_name) {
    const firstName = Array.isArray(claims.value.given_name) ? claims.value.given_name[0] : claims.value.given_name
    const lastName = Array.isArray(claims.value.family_name) ? claims.value.family_name[0] : claims.value.family_name
    userName = `${firstName} ${lastName}`
  } else if (claims.value.preferred_username) {
    userName = Array.isArray(claims.value.preferred_username) ? claims.value.preferred_username[0] : claims.value.preferred_username
  } else if (claims.value.email) {
    // Use email as fallback, but extract just the first email if it's an array
    const email = Array.isArray(claims.value.email) ? claims.value.email[0] : claims.value.email
    // Convert email to a prettier display name
    userName = email.split('@')[0].replace('.', ' ').replace('_', ' ')
    // Capitalize first letters
    userName = userName.split(' ').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ')
  } else {
    userName = 'User'
  }
  
  return userName
}

onMounted(() => {
  checkAuthStatus()
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.logo-section h1 {
  color: #1f2937;
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.logo-section p {
  color: #6b7280;
  margin: 0 0 32px 0;
  font-size: 1rem;
}

.login-btn {
  width: 100%;
  background: #667eea;
  color: white;
  border: none;
  padding: 16px 24px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: #5a67d8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.loading-state {
  padding: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  color: #6b7280;
  margin: 0;
}

.success-state {
  padding: 20px;
}

.success-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.success-state p {
  color: #1f2937;
  margin: 8px 0;
  font-weight: 600;
}

.redirect-text {
  color: #6b7280 !important;
  font-weight: 400 !important;
  font-size: 0.9rem;
}
</style>
