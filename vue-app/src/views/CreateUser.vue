<template>
  <div class="user-tools-page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <p>Loading user data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p>Error loading user data: {{ error }}</p>
      <router-link to="/onboarding" class="btn-primary">
        <i class="fa-solid fa-arrow-left"></i> Back to Onboarding
      </router-link>
    </div>

    <!-- Main Content -->
    <div v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <div class="header-text">
            <h1>User Management Tools</h1>
            <p>Execute scripts for {{ userData?.first_name }} {{ userData?.last_name }} - {{ userData?.email }}</p>
          </div>
          <router-link to="/onboarding" class="add-new-btn">
            <i class="fa-solid fa-arrow-left"></i> Back to Onboarding
          </router-link>
        </div>
      </div>

      <!-- User Information Section -->
      <div class="content-section">
        <div class="section-header">
          <h2>User Information</h2>
        </div>
        <div class="user-info-content">
          <div class="user-info-grid">
            <div class="info-field">
              <label>First Name</label>
              <div class="field-value">{{ userData?.first_name || 'N/A' }}</div>
            </div>
            <div class="info-field">
              <label>Last Name</label>
              <div class="field-value">{{ userData?.last_name || 'N/A' }}</div>
            </div>
            <div class="info-field">
              <label>Username</label>
              <div class="field-value">{{ userData?.username || 'N/A' }}</div>
            </div>
            <div class="info-field">
              <label>Title</label>
              <div class="field-value">{{ userData?.title || 'N/A' }}</div>
            </div>
            <div class="info-field">
              <label>Department</label>
              <div class="field-value">{{ userData?.department || 'N/A' }}</div>
            </div>
            <div class="info-field">
              <label>Manager's Email</label>
              <div class="field-value">{{ userData?.manager || userData?.managers || 'N/A' }}</div>
            </div>
            <div class="info-field">
              <label>Start Date</label>
              <div class="field-value">{{ formatDate(userData?.start_date) }}</div>
            </div>
            <div class="info-field">
              <label>Status</label>
              <div class="field-value">
                <span class="status-badge" :class="getStatusClass(userData?.status)">
                  {{ userData?.status || 'N/A' }}
                </span>
              </div>
            </div>
            <div class="info-field">
              <label>Password</label>
              <div class="field-value">{{ userData?.password || 'N/A' }}</div>
            </div>
            <div class="info-field">
              <label>Department OU</label>
              <div class="field-value">{{ userData?.department_ou || userData?.ou || 'N/A' }}</div>
            </div>
            <div class="info-field">
              <label>Credit9.com Alias</label>
              <div class="field-value">{{ userData?.credit9_alias || userData?.credit9_com_alias || 'N/A' }}</div>
            </div>
            <div class="info-field">
              <label>Advantageteam.law Alias</label>
              <div class="field-value">{{ userData?.advantageteam_alias || userData?.advantageteam_law_alias || 'N/A' }}</div>
            </div>
            <div class="info-field">
              <label>System Hostname</label>
              <div class="field-value">{{ userData?.hostname || 'N/A' }}</div>
            </div>
          </div>
        </div>
      </div>

    <!-- Script Execution Section -->
      <!-- Available Scripts Section -->
      <div class="content-section">
        <div class="section-header">
          <h2>Available Scripts</h2>
        </div>
        <div class="scripts-content">      <!-- JumpCloud Scripts -->
      <div class="script-category">
        <h4>🔗 JumpCloud Operations</h4>
        <div class="script-buttons">
          <button 
            @click="executeScript('jumpcloud', 'create_user')"
            class="script-btn jumpcloud"
            :disabled="isExecuting"
          >
            <span class="btn-icon">👤</span>
            <div class="btn-content">
              <div class="btn-title">Create User JumpCloud</div>
              <div class="btn-description">Create user account in JumpCloud directory</div>
            </div>
          </button>
          
          <button 
            @click="executeScript('jumpcloud', 'bind_machine')"
            class="script-btn jumpcloud"
            :disabled="isExecuting"
          >
            <span class="btn-icon">💻</span>
            <div class="btn-content">
              <div class="btn-title">Bind Machine to User</div>
              <div class="btn-description">Associate a machine with the user account</div>
            </div>
          </button>
        </div>
      </div>

      <!-- Google Workspace Scripts -->
      <div class="script-category">
        <h4>🔵 Google Workspace Operations</h4>
        <div class="script-buttons">
          <button 
            @click="executeScript('google', 'create_user')"
            class="script-btn google"
            :disabled="isExecuting"
          >
            <span class="btn-icon">👤</span>
            <div class="btn-content">
              <div class="btn-title">Create User Google</div>
              <div class="btn-description">Create user account in Google Workspace</div>
            </div>
          </button>
          
          <button 
            @click="executeScript('google', 'add_aliases')"
            class="script-btn google"
            :disabled="isExecuting"
          >
            <span class="btn-icon">📧</span>
            <div class="btn-content">
              <div class="btn-title">Add Google Aliases</div>
              <div class="btn-description">Add email aliases to Google account</div>
            </div>
          </button>
          
          <button 
            @click="executeScript('google', 'force_password_change')"
            class="script-btn google"
            :disabled="isExecuting"
          >
            <span class="btn-icon">🔐</span>
            <div class="btn-content">
              <div class="btn-title">Force Password Change</div>
              <div class="btn-description">Require password change at next login</div>
            </div>
          </button>
        </div>
      </div>
      </div> <!-- Close scripts-content -->
      </div> <!-- Close content-section -->

      <!-- Execution Results Section -->
      <div v-if="executionResults.length > 0" class="content-section">
        <div class="section-header">
          <h2>Execution Results</h2>
        </div>
        <div class="results-content">
          <div v-for="(result, index) in executionResults" 
               :key="index"
               class="result-item"
               :class="{ success: result.success, error: !result.success }"
          >
            <div class="result-header">
              <span class="result-icon">{{ result.success ? '✅' : '❌' }}</span>
              <div class="result-info">
                <div class="result-title">{{ result.script_type }} - {{ result.script_name }}</div>
                <div class="result-time">{{ formatDateTime(result.executed_at) }}</div>
              </div>
            </div>
            <div v-if="result.output" class="result-output">
              <pre>{{ result.output }}</pre>
            </div>
            <div v-if="result.error" class="result-error">
              <strong>Error:</strong> {{ result.error }}
            </div>
          </div>
        </div>
      </div>

    <!-- Loading Overlay -->
    <div v-if="isExecuting" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>Executing {{ currentScript }}...</p>
      </div>
    </div>
    </div> <!-- Close main content div -->
  </div>
</template>

<script>
export default {
  name: 'CreateUser',
  data() {
    return {
      userData: null,
      loading: true,
      error: null,
      isExecuting: false,
      currentScript: '',
      executionResults: []
    }
  },
  async mounted() {
    await this.fetchUserData()
  },
  methods: {
    async fetchUserData() {
      try {
        const userId = this.$route.params.userId
        const response = await fetch(`/api/v1/onboarding/${userId}`)
        if (!response.ok) {
          throw new Error('Failed to fetch user data')
        }
        this.userData = await response.json()
        console.log('User data received:', this.userData)
      } catch (error) {
        console.error('Error fetching user data:', error)
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async executeScript(scriptType, scriptName) {
      this.isExecuting = true
      this.currentScript = `${scriptType} - ${scriptName}`
      
      try {
        const requestBody = {
          script_type: scriptType,
          script_name: scriptName,
          user_id: this.userData.id,
          additional_params: this.getAdditionalParams(scriptType, scriptName)
        }

        const userEmail = this.getCurrentUserEmail()
        const response = await fetch(`/api/v1/scripts/execute?user_email=${encodeURIComponent(userEmail)}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        })

        const result = await response.json()
        
        if (!response.ok) {
          throw new Error(result.detail || 'Script execution failed')
        }

        // Add result to the top of the list
        this.executionResults.unshift(result)
        
        // Limit to last 10 results
        if (this.executionResults.length > 10) {
          this.executionResults = this.executionResults.slice(0, 10)
        }

      } catch (error) {
        console.error('Script execution error:', error)
        
        // Add error result
        this.executionResults.unshift({
          success: false,
          error: error.message,
          output: '',
          script_type: scriptType,
          script_name: scriptName,
          executed_at: new Date().toISOString()
        })
      } finally {
        this.isExecuting = false
        this.currentScript = ''
      }
    },

    getAdditionalParams(scriptType, scriptName) {
      // Return additional parameters based on script type and name
      const params = {}
      
      if (scriptType === 'google' && scriptName === 'add_aliases') {
        // For aliases, you might want to prompt or use predefined aliases
        params.aliases = [
          `${this.userData.first_name.toLowerCase()}.${this.userData.last_name.toLowerCase()}@company.com`,
          `${this.userData.first_name.toLowerCase()}@company.com`
        ]
      }
      
      if (scriptType === 'jumpcloud' && scriptName === 'bind_machine') {
        // For machine binding, you might want to prompt for machine name
        params.hostname = `${this.userData.first_name.toLowerCase()}-laptop`
      }
      
      return params
    },

    getCurrentUserEmail() {
      // Get current user email from session storage or other source
      const userClaims = sessionStorage.getItem('userClaims')
      if (userClaims) {
        try {
          const claims = JSON.parse(userClaims)
          return claims.email || 'admin@company.com'
        } catch {
          return 'admin@company.com'
        }
      }
      return 'admin@company.com'
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },

    formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    },

    getStatusClass(status) {
      if (!status) return ''
      
      const statusLower = status.toLowerCase()
      if (statusLower === 'pending') return 'pending'
      if (statusLower === 'in_progress' || statusLower === 'in progress') return 'in_progress'
      if (statusLower === 'completed') return 'completed'
      return ''
    }
  }
}
</script>

<style scoped>
/* OnboardingView-style layout */
.user-tools-page {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text h1 {
  margin: 0 0 4px 0;
  color: #1f2937;
  font-size: 1.75rem;
  font-weight: 600;
}

.header-text p {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.content-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.section-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.3rem;
  font-weight: 600;
}

.close-btn {
  background: #64748b;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  text-decoration: none;
}

.close-btn:hover {
  background: #475569;
  transform: translateY(-1px);
}

.close-btn i {
  font-size: 12px;
}

/* Add New Button Style */
.add-new-btn {
  background: #d946ef;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  text-decoration: none;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}


.add-new-btn i {
  font-size: 14px;
}

/* User Information Section */
.user-info-content {
  padding: 20px;
}

.user-info-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
}

@media (max-width: 1200px) {
  .user-info-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .user-info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .user-info-grid {
    grid-template-columns: 1fr;
  }
}

.info-field {
  display: flex;
  flex-direction: column;
}

.info-field label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 4px;
}

.field-value {
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.875rem;
  color: #111827;
  min-height: 20px;
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-badge.pending {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.in_progress {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-badge.completed {
  background-color: #d1fae5;
  color: #065f46;
}

/* Scripts Section */
.scripts-content {
  padding: 20px;
}

.script-category {
  margin-bottom: 24px;
}

.script-category h4 {
  margin: 0 0 12px 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.script-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 12px;
}

.script-btn {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.script-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.script-btn.jumpcloud {
  border-color: #667eea;
}

.script-btn.jumpcloud:hover:not(:disabled) {
  border-color: #5a67d8;
  background: #f7fafc;
}

.script-btn.google {
  border-color: #10b981;
}

.script-btn.google:hover:not(:disabled) {
  border-color: #059669;
  background: #f0fdf4;
}

.script-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.btn-content {
  flex: 1;
}

.btn-title {
  font-weight: 600;
  color: #1f2937;
  font-size: 1rem;
  margin-bottom: 4px;
}

.btn-description {
  color: #6b7280;
  font-size: 0.85rem;
  line-height: 1.4;
}

/* Results Section */
.results-content {
  padding: 20px;
}

.result-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  border-left: 4px solid #e5e7eb;
}

.result-item.success {
  border-left-color: #10b981;
}

.result-item.error {
  border-left-color: #ef4444;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.result-icon {
  font-size: 1.2rem;
}

.result-info {
  flex: 1;
}

.result-title {
  font-weight: 600;
  color: #1f2937;
  text-transform: capitalize;
}

.result-time {
  color: #6b7280;
  font-size: 0.85rem;
}

.result-output {
  background: #f3f4f6;
  border-radius: 6px;
  padding: 12px;
  margin-top: 8px;
}

.result-output pre {
  margin: 0;
  font-size: 0.85rem;
  white-space: pre-wrap;
  word-break: break-word;
}

.result-error {
  color: #dc2626;
  background: #fef2f2;
  border-radius: 6px;
  padding: 12px;
  margin-top: 8px;
  font-size: 0.9rem;
}

/* Loading States */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  padding: 40px;
  text-align: center;
}

.error-state {
  color: #dc2626;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content {
  text-align: center;
  padding: 32px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-content p {
  margin: 0;
  color: #6b7280;
  font-weight: 500;
}
</style>
