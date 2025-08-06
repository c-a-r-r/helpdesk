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
            <h1>Onboarding Tools</h1>
            <p>Execute scripts for {{ userData?.first_name }} {{ userData?.last_name }}</p>
          </div>
          <button class="btn-secondary" @click="goBack">
            <i class="fa-solid fa-arrow-left"></i> Back to Onboarding
          </button>
        </div>
      </div>

      <!-- User Information Section -->
      <div class="content-section">
        <div class="user-form-container">
          <div class="section-title">
            <h2>User Information</h2>
          </div>
          <div class="form-grid">
            <!-- Company -->
            <div class="form-group">
              <label>Company</label>
              <input type="text" :value="userData?.company || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- First Name -->
            <div class="form-group">
              <label>First Name</label>
              <input type="text" :value="userData?.first_name || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Last Name -->
            <div class="form-group">
              <label>Last Name</label>
              <input type="text" :value="userData?.last_name || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Display Name -->
            <div class="form-group">
              <label>Display Name</label>
              <input type="text" :value="userData?.display_name || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Company Email -->
            <div class="form-group">
              <label>Company Email</label>
              <input type="email" :value="userData?.company_email || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Title -->
            <div class="form-group">
              <label>Title</label>
              <input type="text" :value="userData?.title || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Manager -->
            <div class="form-group">
              <label>Manager</label>
              <input type="text" :value="userData?.manager || userData?.managers || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Department -->
            <div class="form-group">
              <label>Department</label>
              <input type="text" :value="userData?.department || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Username -->
            <div class="form-group">
              <label>Username</label>
              <input type="text" :value="userData?.username || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Password -->
            <div class="form-group">
              <label>Password</label>
              <input type="text" :value="userData?.password || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Department OU -->
            <div class="form-group">
              <label>Department OU</label>
              <input type="text" :value="userData?.department_ou || userData?.ou || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Credit9 Alias -->
            <div class="form-group">
              <label>Credit9.com Alias</label>
              <input type="text" :value="userData?.credit9_alias || userData?.credit9_com_alias || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Advantageteam Alias -->
            <div class="form-group">
              <label>Advantageteam.law Alias</label>
              <input type="text" :value="userData?.advantageteam_alias || userData?.advantageteam_law_alias || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Hostname -->
            <div class="form-group">
              <label>System Hostname</label>
              <input type="text" :value="userData?.hostname || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Start Date -->
            <div class="form-group">
              <label>Start Date</label>
              <input type="text" :value="formatDate(userData?.start_date)" readonly class="readonly-field">
            </div>
            
            <!-- Notes -->
            <div class="form-group">
              <label>Notes</label>
              <textarea :value="userData?.notes || 'N/A'" readonly class="readonly-field" rows="3"></textarea>
            </div>
            
            <!-- Extra Details -->
            <div class="form-group">
              <label>Extra Details</label>
              <textarea :value="userData?.extra_details || 'N/A'" readonly class="readonly-field" rows="3"></textarea>
            </div>
            
            <!-- Created By -->
            <div class="form-group">
              <label>Created By</label>
              <input type="text" :value="userData?.created_by || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Created Date -->
            <div class="form-group">
              <label>Created Date</label>
              <input type="text" :value="formatDateTime(userData?.created_at)" readonly class="readonly-field">
            </div>
          </div>
        </div>
      </div>

      <!-- Available Scripts Section -->
      <div class="content-section">
        <div class="user-form-container">
          <div class="section-title">
            <h2>Available Scripts</h2>
          </div>
          <div class="scripts-grid">
            <!-- JumpCloud Scripts -->
            <div class="script-group">
              <h3>🔗 JumpCloud Operations</h3>
              <div class="script-list">
                <button 
                  @click="executeScript('jumpcloud', 'create_user')"
                  class="script-btn jumpcloud"
                  :disabled="isExecuting"
                >
                  <span class="btn-icon">👤</span>
                  <span class="btn-text">Create User</span>
                </button>
                
                <button 
                  @click="executeScript('jumpcloud', 'bind_machine')"
                  class="script-btn jumpcloud"
                  :disabled="isExecuting"
                >
                  <span class="btn-icon">💻</span>
                  <span class="btn-text">Bind Machine</span>
                </button>
              </div>
            </div>

            <!-- Google Workspace Scripts -->
            <div class="script-group">
              <h3>🔵 Google Workspace Operations</h3>
              <div class="script-list">
                <button 
                  @click="executeScript('google', 'create_user')"
                  class="script-btn google"
                  :disabled="isExecuting"
                >
                  <span class="btn-icon">👤</span>
                  <span class="btn-text">Create User</span>
                </button>
                
                <button 
                  @click="executeScript('google', 'add_aliases')"
                  class="script-btn google"
                  :disabled="isExecuting"
                >
                  <span class="btn-icon">📧</span>
                  <span class="btn-text">Add Aliases</span>
                </button>
                
                <button 
                  @click="executeScript('google', 'force_password_change')"
                  class="script-btn google"
                  :disabled="isExecuting"
                >
                  <span class="btn-icon">🔐</span>
                  <span class="btn-text">Force Password Change</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Execution Logs Section -->
      <div class="content-section">
        <div class="user-form-container">
          <div class="section-title">
            <h2>Execution Logs</h2>
          </div>
          <div class="logs-content">
            <div v-if="executionResults.length === 0" class="no-logs">
              <p>No script executions recorded yet.</p>
            </div>
            <div v-else class="logs-container">
              <div v-for="(result, index) in executionResults" 
                   :key="index"
                   class="log-entry"
                   :class="{ success: result.success, error: !result.success }"
              >
                <div class="log-header">
                  <div class="log-basic">
                    <span class="status-icon">{{ result.success ? '✅' : '❌' }}</span>
                    <span class="script-name">{{ result.script_type }} - {{ result.script_name }}</span>
                    <span class="time-text">{{ formatDateTime(result.executed_at) }}</span>
                    <span class="user-text">{{ result.executed_by || 'System' }}</span>
                  </div>
                  <button 
                    @click="toggleLogExpanded(index)"
                    class="expand-btn"
                    v-if="result.output || result.error"
                  >
                    {{ result.expanded ? '▼' : '▶' }} 
                    {{ result.expanded ? 'Hide' : 'Show' }} Details
                  </button>
                </div>
                
                <div v-if="result.expanded && (result.output || result.error)" class="log-details">
                  <div v-if="result.output" class="output-section">
                    <div class="output-label">Output:</div>
                    <pre class="output-content">{{ result.output }}</pre>
                  </div>
                  <div v-if="result.error" class="error-section">
                    <div class="error-label">Error:</div>
                    <pre class="error-content">{{ result.error }}</pre>
                  </div>
                </div>
                
                <div v-if="!result.output && !result.error" class="no-output">
                  No output available
                </div>
              </div>
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
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserToolsView',
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
    await this.fetchExecutionLogs()
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

    async fetchExecutionLogs() {
      try {
        const userId = this.$route.params.userId
        const response = await fetch(`/api/v1/scripts/logs?user_id=${userId}&limit=20`)
        if (response.ok) {
          const logs = await response.json()
          // Transform backend logs to match frontend format
          this.executionResults = logs.map(log => {
            // Check for success in multiple ways
            let isSuccess = false
            
            // First check the database status
            if (log.status === 'SUCCESS') {
              isSuccess = true
            }
            
            // Also check if the output contains success indicators
            if (log.output) {
              try {
                const outputJson = JSON.parse(log.output)
                if (outputJson.success === true) {
                  // Check if the result nested object indicates failure
                  if (outputJson.result && outputJson.result.status === 'failed') {
                    isSuccess = false
                  } else if (outputJson.result && outputJson.result.error) {
                    isSuccess = false
                  } else {
                    isSuccess = true
                  }
                }
              } catch (e) {
                // If output is not JSON, check for text indicators
                // But also check for failure indicators first
                if (log.output.includes('failed') || 
                    log.output.includes('error') || 
                    log.output.includes('400') ||
                    log.output.includes('500') ||
                    log.output.includes('Failed to create')) {
                  isSuccess = false
                } else if (log.output.includes('"success": true') || 
                           log.output.includes('successfully') || 
                           log.output.includes('created')) {
                  isSuccess = true
                }
              }
            }
            
            return {
              success: isSuccess,
              script_type: log.script_type,
              script_name: log.script_name,
              executed_at: log.started_at,
              executed_by: log.executed_by ? log.executed_by.split(',')[0] : 'System',
              output: log.output || '',
              error: log.error_message || '',
              expanded: false // Add expanded state for each log
            }
          })
          console.log('Execution logs loaded:', this.executionResults.length)
        }
      } catch (error) {
        console.error('Error fetching execution logs:', error)
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
        let userClaims = sessionStorage.getItem('userClaims')
        
        // If no SSO claims available, create mock claims for development
        if (!userClaims) {
          console.warn('No SSO claims found, creating development mock claims')
          const mockClaims = {
            email: userEmail,
            name: 'Cristian Rodriguez',
            given_name: 'Cristian',
            family_name: 'Rodriguez',
            Role: 'Help Desk Management Tool - Admin',
            groups: ['Help Desk Management Tool - Admin']
          }
          userClaims = JSON.stringify(mockClaims)
        }
        
        let apiUrl = `/api/v1/scripts/execute?user_email=${encodeURIComponent(userEmail)}`
        
        // Add SSO claims for permission checking
        apiUrl += `&user_claims=${encodeURIComponent(userClaims)}`
        
        const response = await fetch(apiUrl, {
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

        // Add executed_by field
        result.executed_by = userEmail

        // Refresh logs from backend to get the most up-to-date data
        await this.fetchExecutionLogs()

      } catch (error) {
        console.error('Script execution error:', error)
        
        // Add error result
        this.executionResults.unshift({
          success: false,
          error: error.message,
          output: '',
          script_type: scriptType,
          script_name: scriptName,
          executed_at: new Date().toISOString(),
          executed_by: this.getCurrentUserEmail(),
          expanded: false
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
        params.aliases = [
          this.userData?.credit9_alias || this.userData?.credit9_com_alias,
          this.userData?.advantageteam_alias || this.userData?.advantageteam_law_alias
        ].filter(Boolean)
      }
      
      if (scriptType === 'jumpcloud' && scriptName === 'bind_machine') {
        params.company_email = this.userData?.company_email
        params.hostname = this.userData?.hostname || `${this.userData?.first_name?.toLowerCase()}-laptop`
      }
      
      return params
    },

    toggleLogExpanded(index) {
      this.executionResults[index].expanded = !this.executionResults[index].expanded
    },

    getCurrentUserEmail() {
      // Try to get user data from JumpCloud SSO claims in sessionStorage
      const userClaims = sessionStorage.getItem('userClaims')
      if (userClaims) {
        try {
          const claims = JSON.parse(userClaims)
          console.log('JumpCloud SSO claims received:', claims)
          
          // Try to get email from JumpCloud claims
          if (claims.email) {
            console.log('Found email in claims:', claims.email)
            return claims.email
          }
          
          // Try preferred_username
          if (claims.preferred_username && claims.preferred_username.includes('@')) {
            console.log('Found email in preferred_username:', claims.preferred_username)
            return claims.preferred_username
          }
          
          // If no direct email, construct one from name fields
          if (claims.given_name && claims.family_name) {
            const constructedEmail = `${claims.given_name.toLowerCase()}.${claims.family_name.toLowerCase()}@americor.com`
            console.log('Constructed email from name:', constructedEmail)
            return constructedEmail
          }
          
        } catch (error) {
          console.error('Error parsing JumpCloud SSO claims:', error)
        }
      }
      
      // Check localStorage for any user tokens
      const userToken = localStorage.getItem('userToken')
      if (userToken) {
        try {
          const tokenParts = userToken.split('.')
          if (tokenParts.length === 3) {
            const payload = JSON.parse(atob(tokenParts[1]))
            if (payload.email) {
              console.log('Found email in JWT token:', payload.email)
              return payload.email
            }
            if (payload.preferred_username && payload.preferred_username.includes('@')) {
              console.log('Found email in JWT preferred_username:', payload.preferred_username)
              return payload.preferred_username
            }
          }
        } catch (error) {
          console.error('Error decoding JWT token:', error)
        }
      }
      
      // Development mode fallback - since you're testing as admin
      console.warn('No SSO claims found, using development fallback')
      return 'cristian.rodriguez@americor.com'
    },

    getCurrentUser() {
      // Get full user information from SSO claims
      const userClaims = sessionStorage.getItem('userClaims')
      if (userClaims) {
        try {
          const claims = JSON.parse(userClaims)
          return {
            email: this.getCurrentUserEmail(),
            name: claims.name || `${claims.given_name || ''} ${claims.family_name || ''}`.trim(),
            groups: claims.groups || [],
            isAdmin: this.isCurrentUserAdmin(claims)
          }
        } catch (error) {
          console.error('Error parsing user claims:', error)
        }
      }
      
      // Development fallback
      if (process.env.NODE_ENV === 'development') {
        return {
          email: 'cristian.rodriguez@americor.com',
          name: 'Cristian Rodriguez',
          groups: ['admin'],
          isAdmin: true
        }
      }
      
      return null
    },

    isCurrentUserAdmin(claims = null) {
      // Admin user emails
      const adminUsers = [
        'cristian.rodriguez@americor.com',
        'admin@americor.com'
      ]
      
      const userEmail = this.getCurrentUserEmail()
      
      // Check if user is in admin list
      if (adminUsers.includes(userEmail)) {
        return true
      }
      
      // Check JumpCloud groups
      if (claims && claims.groups) {
        const groups = Array.isArray(claims.groups) ? claims.groups : [claims.groups]
        return groups.some(group => 
          group.toLowerCase().includes('admin') || 
          group.toLowerCase().includes('administrator')
        )
      }
      
      return false
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },

    formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    },

    goBack() {
      this.$router.push({ name: 'onboarding' })
    }
  }
}
</script>

<style scoped>
.user-tools-page {
  padding: 0;
}

.page-header {
  margin-bottom: 12px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text h1 {
  margin: 0 0 2px 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-text p {
  margin: 0;
  color: #6b7280;
  font-size: 0.85rem;
}

.content-section {
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 12px;
}

.user-form-container {
  padding: 16px;
}

.section-title {
  margin-bottom: 12px;
}

.section-title h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.1rem;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 4px;
}

/* Form Grid - 5 fields per row */
.form-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 8px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 2px;
  color: #374151;
  font-weight: 500;
  font-size: 0.8rem;
}

.form-group input,
.form-group textarea {
  padding: 4px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.85rem;
  background: white;
}

.form-group textarea {
  resize: vertical;
  min-height: 50px;
}

.readonly-field {
  background-color: #f9fafb !important;
  color: #6b7280 !important;
  cursor: not-allowed;
}

/* Scripts Section */
.scripts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.script-group {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  background: #f9fafb;
}

.script-group h3 {
  margin: 0 0 8px 0;
  color: #1f2937;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.script-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.script-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  font-size: 0.85rem;
}

.script-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  font-size: 1rem;
  flex-shrink: 0;
}

.btn-text {
  font-weight: 500;
  color: #1f2937;
}

/* Logs Section */
.logs-content {
  min-height: 150px;
}

.no-logs {
  text-align: center;
  padding: 20px;
  color: #6b7280;
  font-size: 0.9rem;
}

.logs-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-entry {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  overflow: hidden;
  transition: all 0.2s ease;
}

.log-entry:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.log-entry.success {
  border-left: 4px solid #10b981;
}

.log-entry.error {
  border-left: 4px solid #ef4444;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f9fafb;
}

.log-basic {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.status-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.script-name {
  font-weight: 600;
  color: #1f2937;
  text-transform: capitalize;
  min-width: 180px;
}

.time-text {
  color: #6b7280;
  font-size: 0.85rem;
  min-width: 140px;
}

.user-text {
  color: #6b7280;
  font-size: 0.85rem;
  min-width: 120px;
}

.expand-btn {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 0.8rem;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.expand-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.log-details {
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  background: white;
}

.output-section,
.error-section {
  margin-bottom: 12px;
}

.output-section:last-child,
.error-section:last-child {
  margin-bottom: 0;
}

.output-label,
.error-label {
  font-weight: 600;
  margin-bottom: 6px;
  font-size: 0.85rem;
}

.output-label {
  color: #059669;
}

.error-label {
  color: #dc2626;
}

.output-content,
.error-content {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.8rem;
  line-height: 1.4;
  color: #1e293b;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
}

.error-content {
  background: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

.no-output {
  color: #9ca3af;
  font-style: italic;
  font-size: 0.85rem;
  padding: 8px 16px;
  text-align: center;
}

/* Button Styles */
.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

.btn-secondary {
  background: #f8fafc;
  color: #475569;
  border: 1px solid #e2e8f0;
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-secondary:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Loading States */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 150px;
  padding: 20px;
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
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-in-out;
}

.loading-content {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  text-align: center;
  min-width: 240px;
  animation: slideIn 0.3s ease-out;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { 
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.loading-content p {
  margin: 0;
  color: #374151;
  font-weight: 600;
  font-size: 1rem;
}

/* Responsive adjustments */
@media (max-width: 1600px) {
  .form-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1400px) {
  .form-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1024px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .scripts-grid {
    grid-template-columns: 1fr;
  }
  
  .log-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .log-basic {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .script-name,
  .time-text,
  .user-text {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .log-basic {
    flex-direction: column;
    gap: 4px;
  }
  
  .user-text {
    display: none;
  }
}
</style>
