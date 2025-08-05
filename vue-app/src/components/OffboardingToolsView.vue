<template>
  <div class="offboarding-tools-page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <p>Loading user data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p>Error loading user data: {{ error }}</p>
      <router-link to="/offboarding" class="btn-primary">
        <i class="fa-solid fa-arrow-left"></i> Back to Offboarding
      </router-link>
    </div>

    <!-- Main Content -->
    <div v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <div class="header-text">
            <h1>Offboarding Tools</h1>
            <p>Execute offboarding scripts for {{ user?.first_name }} {{ user?.last_name }}</p>
          </div>
          <button class="btn-secondary" @click="goBack">
            <i class="fa-solid fa-arrow-left"></i> Back to Offboarding
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
            <!-- First Name -->
            <div class="form-group">
              <label>First Name</label>
              <input type="text" :value="user?.first_name || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Last Name -->
            <div class="form-group">
              <label>Last Name</label>
              <input type="text" :value="user?.last_name || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Company Email -->
            <div class="form-group">
              <label>Company Email</label>
              <input type="email" :value="user?.company_email || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Hostname -->
            <div class="form-group">
              <label>System Hostname</label>
              <input type="text" :value="user?.hostname || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Requested By -->
            <div class="form-group">
              <label>Requested By</label>
              <input type="email" :value="user?.requested_by || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Created By -->
            <div class="form-group">
              <label>Created By</label>
              <input type="text" :value="user?.created_by || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Password -->
            <div class="form-group">
              <label>Password</label>
              <input type="text" :value="user?.password || 'N/A'" readonly class="readonly-field">
            </div>
            
            <!-- Status -->
            <div class="form-group">
              <label>Status</label>
              <input type="text" :value="user?.status || 'N/A'" readonly class="readonly-field" :class="getStatusClass(user?.status)">
            </div>
            
            <!-- Notes -->
            <div class="form-group">
              <label>Notes</label>
              <textarea :value="user?.notes || 'N/A'" readonly class="readonly-field" rows="3"></textarea>
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
                @click="executeScript('jumpcloud', 'terminate_user')"
                class="script-btn jumpcloud"
                :disabled="isExecuting"
              >
                <span class="btn-icon"><i class="fa-solid fa-user-slash"></i></span>
                <span class="btn-text">Terminate User</span>
              </button>
            </div>
          </div>

          <!-- Google Workspace Scripts -->
          <div class="script-group">
            <h3>🔵 Google Workspace Operations</h3>
            <div class="script-list">
              <button 
                @click="executeScript('offboarding', 'terminate_user_google')"
                class="script-btn google"
                :disabled="isExecuting"
              >
                <span class="btn-icon"><i class="fa-solid fa-user-xmark"></i></span>
                <span class="btn-text">Terminate User</span>
              </button>
            </div>
          </div>

          <!-- Automox Scripts -->
          <div class="script-group">
            <h3>🛡️ Automox Operations</h3>
            <div class="script-list">
              <button 
                @click="executeScript('offboarding', 'remove_automox_agent')"
                class="script-btn automox"
                :disabled="isExecuting"
              >
                <span class="btn-icon"><i class="fa-solid fa-desktop"></i></span>
                <span class="btn-text">Remove Agent</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Script Output Section -->
    <div v-if="lastExecution" class="content-section">
      <div class="user-form-container">
        <div class="section-title">
          <h2>Script Output</h2>
          <span :class="getExecutionStatusClass(lastExecution.success)">
            {{ lastExecution.success ? 'Success' : 'Failed' }}
          </span>
        </div>
        
        <div class="output-content">
          <div class="execution-info">
            <p><strong>Script:</strong> {{ lastExecution.script_name }}</p>
            <p><strong>Executed at:</strong> {{ formatDate(lastExecution.executed_at) }}</p>
            <p><strong>Executed by:</strong> {{ lastExecution.executed_by }}</p>
          </div>
          
          <div class="output-text">
            <pre>{{ lastExecution.output }}</pre>
          </div>
          
          <div v-if="lastExecution.error" class="error-text">
            <h4>Error Details:</h4>
            <pre>{{ lastExecution.error }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Execution Logs Section -->
    <div class="content-section">
      <div class="user-form-container">
        <div class="section-title">
          <h2>Execution Logs</h2>
          <button class="btn-secondary" @click="fetchScriptLogs">
            <i class="fa-solid fa-arrows-rotate"></i> Refresh
          </button>
        </div>
        <div class="logs-content">
          <div v-if="loadingLogs" class="loading-state">
            <p>Loading script logs...</p>
          </div>
          
          <div v-else-if="scriptLogs.length === 0" class="no-logs">
            <p>No script executions recorded yet.</p>
          </div>
          
          <div v-else class="logs-container">
            <div v-for="(log, index) in scriptLogs" 
                 :key="log.id"
                 class="log-entry"
                 :class="{ success: isLogSuccess(log), error: !isLogSuccess(log) }"
            >
              <div class="log-header">
                <div class="log-basic">
                  <span class="status-icon">{{ isLogSuccess(log) ? '✅' : '❌' }}</span>
                  <span class="script-name">{{ log.script_type }} - {{ log.script_name }}</span>
                  <span class="time-text">{{ formatDateTime(log.started_at) }}</span>
                  <span class="user-text">{{ log.executed_by || 'System' }}</span>
                </div>
                <button 
                  @click="toggleLogExpanded(index)"
                  class="expand-btn"
                  v-if="log.output || log.error_message"
                >
                  {{ log.expanded ? '▼' : '▶' }} 
                  {{ log.expanded ? 'Hide' : 'Show' }} Details
                </button>
              </div>
              
              <div v-if="log.expanded && (log.output || log.error_message)" class="log-details">
                <div v-if="log.output" class="output-section">
                  <div class="output-label">Output:</div>
                  <pre class="output-content">{{ log.output }}</pre>
                </div>
                <div v-if="log.error_message" class="error-section">
                  <div class="error-label">Error:</div>
                  <pre class="error-content">{{ log.error_message }}</pre>
                </div>
              </div>
              
              <div v-if="!log.output && !log.error_message" class="no-output">
                No output available
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'OffboardingToolsView',
  data() {
    return {
      user: null,
      loading: true,
      isExecuting: false,
      lastExecution: null,
      scriptLogs: [],
      loadingLogs: false,
      error: null
    }
  },
  async mounted() {
    await this.fetchUser()
    await this.fetchScriptLogs()
  },
  methods: {
    async fetchUser() {
      try {
        const userId = this.$route.params.userId
        const response = await axios.get(`/api/v1/offboarding/${userId}`)
        this.user = response.data
      } catch (error) {
        console.error('Error fetching user:', error)
        this.error = 'Failed to load user information'
      } finally {
        this.loading = false
      }
    },
    async fetchScriptLogs() {
      this.loadingLogs = true
      try {
        const offboardingId = this.$route.params.userId
        const response = await axios.get(`/api/v1/offboarding/${offboardingId}/script-logs?limit=20`)
        if (response.status === 200) {
          // Add expanded state to each log
          this.scriptLogs = response.data.map(log => ({
            ...log,
            expanded: false
          }))
        }
      } catch (error) {
        console.error('Error fetching script logs:', error)
      } finally {
        this.loadingLogs = false
      }
    },
    
    toggleLogExpanded(index) {
      this.scriptLogs[index].expanded = !this.scriptLogs[index].expanded
    },
    
    isLogSuccess(log) {
      // Check status first
      if (log.status === 'SUCCESS' || log.status === 'success') {
        return true
      }
      if (log.status === 'FAILED' || log.status === 'failed' || log.status === 'ERROR') {
        return false
      }
      
      // Check output for success indicators if status is ambiguous
      if (log.output) {
        try {
          const outputJson = JSON.parse(log.output)
          if (outputJson.success === true) {
            // Check if nested result indicates failure
            if (outputJson.result && outputJson.result.status === 'failed') {
              return false
            } else if (outputJson.result && outputJson.result.error) {
              return false
            }
            return true
          }
        } catch (e) {
          // If output is not JSON, check for text indicators
          if (log.output.includes('failed') || 
              log.output.includes('error') || 
              log.output.includes('400') ||
              log.output.includes('500') ||
              log.output.includes('Failed')) {
            return false
          } else if (log.output.includes('"success": true') || 
                     log.output.includes('successfully') || 
                     log.output.includes('completed')) {
            return true
          }
        }
      }
      
      // Default to false if we can't determine success
      return false
    },
    
    formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    },
    async executeScript(scriptType, scriptName) {
      this.isExecuting = true
      try {
        const offboardingId = this.$route.params.userId
        const currentUserEmail = this.getCurrentUserEmail()
        
        const response = await axios.post(`/api/v1/offboarding/${offboardingId}/execute-script?user_email=${encodeURIComponent(currentUserEmail)}`, {
          script_type: scriptType,
          script_name: scriptName,
          additional_params: {
            offboarding_id: parseInt(offboardingId)
          }
        })
        
        this.lastExecution = response.data
        
        // Refresh logs after execution
        this.fetchScriptLogs()
        
        // If this was a successful deactivation, update user status
        if (response.data.success && (scriptName === 'deactivate_user' || scriptName === 'suspend_user')) {
          this.user.status = 'In Progress'
        }
        
      } catch (error) {
        console.error('Error executing script:', error)
        this.lastExecution = {
          success: false,
          output: '',
          error: error.response?.data?.detail || 'Script execution failed',
          executed_by: 'Current User',
          executed_at: new Date().toISOString(),
          script_name: scriptName,
          script_type: scriptType
        }
      } finally {
        this.isExecuting = false
      }
    },
    getStatusClass(status) {
      const statusMap = {
        'Pending': 'status-pending',
        'In Progress': 'status-in-progress', 
        'Completed': 'status-completed',
        'Failed': 'status-failed',
        'success': 'status-completed',
        'failed': 'status-failed',
        'running': 'status-in-progress'
      }
      return statusMap[status] || 'status-pending'
    },
    getExecutionStatusClass(success) {
      return success ? 'execution-success' : 'execution-failed'
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    },
    goBack() {
      this.$router.push({ name: 'offboarding' })
    },
    getCurrentUserEmail() {
      // Development fallback
      if (process.env.NODE_ENV === 'development') {
        return 'cristian.rodriguez@americor.com'
      }
      
      // Try to get user data from JumpCloud SSO claims
      const userClaims = sessionStorage.getItem('userClaims')
      if (userClaims) {
        try {
          const claims = JSON.parse(userClaims)
          if (claims.email) {
            const email = Array.isArray(claims.email) ? claims.email[0] : claims.email
            return email
          }
          if (claims.preferred_username && claims.preferred_username.includes('@')) {
            const email = Array.isArray(claims.preferred_username) ? claims.preferred_username[0] : claims.preferred_username
            return email
          }
        } catch (error) {
          console.error('Error parsing SSO claims:', error)
        }
      }
      
      throw new Error('User not authenticated')
    }
  }
}
</script>

<style scoped>
.offboarding-tools-page {
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
  grid-template-columns: repeat(3, 1fr);
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

.script-btn.automox {
  border-color: #f59e0b;
}

.script-btn.automox:hover:not(:disabled) {
  border-color: #d97706;
  background: #fffbeb;
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
  text-decoration: none;
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

/* Status Classes */
.status-pending {
  background-color: #fef3c7 !important;
  color: #92400e !important;
}

.status-in-progress {
  background-color: #dbeafe !important;
  color: #1e40af !important;
}

.status-completed {
  background-color: #d1fae5 !important;
  color: #065f46 !important;
}

.status-failed {
  background-color: #fee2e2 !important;
  color: #991b1b !important;
}

/* Output Section Styles */
.execution-info {
  background: #f9fafb;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.execution-info p {
  margin: 4px 0;
  color: #6b7280;
  font-size: 0.85rem;
}

.output-text pre {
  background: #1f2937;
  color: #f9fafb;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.8rem;
  line-height: 1.4;
}

.error-text {
  margin-top: 12px;
}

.error-text h4 {
  color: #dc2626;
  margin: 0 0 6px 0;
  font-size: 0.9rem;
}

.error-text pre {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.execution-success {
  background: #f0fdf4;
  color: #16a34a;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.execution-failed {
  background: #fef2f2;
  color: #dc2626;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

/* Table Styles */
.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.data-table th,
.data-table td {
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.85rem;
}

.data-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table tr:hover {
  background: #f9fafb;
}

.empty-state {
  padding: 20px;
  text-align: center;
  color: #6b7280;
  font-size: 0.9rem;
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
