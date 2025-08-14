<template>
  <div class="offboarding-tools-page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <p>Loading user data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p>Error loading user data: {{ error }}</p>
      <router-link to="/offboarding" class="btn-secondary">
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
            <div class="script-header">
              <h3><i class="fa-solid fa-user"></i> JumpCloud Operations</h3>
              <div class="status-badge-container">
                <span class="status-label">JumpCloud Status:</span>
                <span :class="getScriptStatusClass('jumpcloud')" class="status-badge">
                  {{ getScriptStatusText('jumpcloud') }}
                </span>
              </div>
            </div>
            <div class="script-list">
              <button 
                @click="executeScript('jumpcloud', 'terminate_user')"
                class="btn-primary jumpcloud"
                :disabled="isExecuting"
              >
                <span class="btn-icon"><i class="fa-solid fa-user-slash"></i></span>
                <span class="btn-text">Terminate User</span>
              </button>
            </div>
          </div>

          <!-- Google Workspace Scripts -->
          <div class="script-group">
            <div class="script-header">
              <h3><i class="fa-brands fa-google"></i>Google Workspace Operations</h3>
              <div class="status-badge-container">
                <span class="status-label">Google Status:</span>
                <span :class="getScriptStatusClass('google')" class="status-badge">
                  {{ getScriptStatusText('google') }}
                </span>
              </div>
            </div>
            <div class="script-list">
              <button 
                @click="executeScript('offboarding', 'terminate_user_google')"
                class="btn-primary google"
                :disabled="isExecuting"
              >
                <span class="btn-icon"><i class="fa-solid fa-user-xmark"></i></span>
                <span class="btn-text">Terminate User</span>
              </button>
            </div>
          </div>

          <!-- Automox Scripts -->
          <div class="script-group">
            <div class="script-header">
              <h3><i class="fa-solid fa-user-astronaut"></i> Automox Operations</h3>
              <div class="status-badge-container">
                <span class="status-label">Automox Status:</span>
                <span :class="getScriptStatusClass('automox')" class="status-badge">
                  {{ getScriptStatusText('automox') }}
                </span>
              </div>
            </div>
            <div class="script-list">
              <button 
                @click="executeScript('automox', 'remove_agent')"
                class="btn-primary automox"
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
          <button class="btn-secondary" @click="fetchScriptLogs" style="margin-top: 10px;">
            <i class="fa-solid fa-arrows-rotate" ></i> Refresh
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
                 :class="getLogStatusClass(log)"
            >
              <div class="log-header">
                <div class="log-basic">
                  <span class="status-icon">{{ getStatusIcon(log) }}</span>
                  <span class="script-name">{{ log.script_type }} - {{ log.script_name }}</span>
                  <span class="status-badge" :class="getStatusBadgeClass(log)">
                    {{ getDetailedStatus(log) }}
                  </span>
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

    <!-- Loading Overlay -->
    <div v-if="isExecuting" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>Executing script...</p>
        <div class="loading-details">
          <small>This may take a few moments to complete</small>
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
    
    getDetailedStatus(log) {
      const scriptType = log.script_type.toLowerCase()
      
      // First check the database status field if available
      if (log.status === 'SUCCESS' || log.status === 'success') {
        return scriptType === 'automox' ? 'Agent Removed' : 'User Terminated'
      } else if (log.status === 'WARNING' || log.status === 'warning') {
        return scriptType === 'automox' ? 'Agent Not Found' : 'User Not Found'
      } else if (log.status === 'FAILED' || log.status === 'failed' || log.status === 'ERROR') {
        // For failed status, check the output to determine the specific failure reason
        if (log.output || log.error_message) {
          const outputText = (log.output || log.error_message || '').toLowerCase()
          
          // Check for "user not found" or "agent not found" in the output
          if (outputText.includes('user not found') || outputText.includes('no jumpcloud user found') || 
              outputText.includes('not found in jumpcloud') || outputText.includes('agent not found')) {
            return scriptType === 'automox' ? 'Agent Not Found' : 'User Not Found'
          }
        }
        
        // Default failure messages
        return scriptType === 'automox' ? 'Removal Failed' : 'Termination Failed'
      }
      
      // Fallback: Parse the output JSON if status is not clear
      if (log.output) {
        try {
          let outputJson = null
          
          // Handle cases where output might have extra text before JSON
          const jsonMatch = log.output.match(/\{"success".*\}/)
          if (jsonMatch) {
            outputJson = JSON.parse(jsonMatch[0])
          } else {
            // Try parsing the whole output as JSON
            outputJson = JSON.parse(log.output)
          }
          
          if (outputJson) {
            // Check top-level success first
            if (outputJson.success === false) {
              // Check error message for specific failure types
              const errorMsg = (outputJson.error || '').toLowerCase()
              if (errorMsg.includes('user not found') || errorMsg.includes('not found in jumpcloud') || 
                  errorMsg.includes('agent not found')) {
                return scriptType === 'automox' ? 'Agent Not Found' : 'User Not Found'
              }
              return scriptType === 'automox' ? 'Removal Failed' : 'Termination Failed'
            } else if (outputJson.success === true) {
              // Check nested result status
              const nestedResult = outputJson.result || {}
              if (nestedResult.status) {
                const resultStatus = nestedResult.status.toLowerCase()
                if (resultStatus === 'completed' || resultStatus === 'success') {
                  return scriptType === 'automox' ? 'Agent Removed' : 'User Terminated'
                } else if (resultStatus === 'warning') {
                  return scriptType === 'automox' ? 'Agent Not Found' : 'User Not Found'
                } else if (resultStatus === 'failed') {
                  return scriptType === 'automox' ? 'Removal Failed' : 'Termination Failed'
                }
              }
              // Default success case
              return scriptType === 'automox' ? 'Agent Removed' : 'User Terminated'
            }
          }
        } catch (e) {
          // Handle non-JSON output or parsing errors
          const output = log.output.toLowerCase()
          
          if (output.includes('not found')) {
            return scriptType === 'automox' ? 'Agent Not Found' : 'User Not Found'
          } else if (output.includes('successfully') || output.includes('completed')) {
            return scriptType === 'automox' ? 'Agent Removed' : 'User Terminated'
          } else if (output.includes('failed') || output.includes('error')) {
            return scriptType === 'automox' ? 'Removal Failed' : 'Termination Failed'
          }
        }
      }
      
      return 'Unknown'
    },
    
    getStatusIcon(log) {
      const status = this.getDetailedStatus(log)
      
      if (status.includes('Removed') || status.includes('Terminated') || status === 'Success') {
        return '✅'
      } else if (status.includes('Not Found') || status === 'Warning') {
        return '⚠️'
      } else if (status.includes('Failed') || status === 'Failed') {
        return '❌'
      } else {
        return '❓'
      }
    },
    
    getLogStatusClass(log) {
      const status = this.getDetailedStatus(log)
      
      if (status.includes('Removed') || status.includes('Terminated') || status === 'Success') {
        return 'log-success'
      } else if (status.includes('Not Found') || status === 'Warning') {
        return 'log-warning'
      } else if (status.includes('Failed') || status === 'Failed') {
        return 'log-error'
      } else {
        return 'log-unknown'
      }
    },
    
    getStatusBadgeClass(log) {
      const status = this.getDetailedStatus(log)
      
      if (status.includes('Removed') || status.includes('Terminated') || status === 'Success') {
        return 'badge-success'
      } else if (status.includes('Not Found') || status === 'Warning') {
        return 'badge-warning'
      } else if (status.includes('Failed') || status === 'Failed') {
        return 'badge-error'
      } else {
        return 'badge-unknown'
      }
    },
    
    getScriptStatusText(scriptType) {
      if (!this.user) return 'NOT RUN YET'
      
      let status = null
      if (scriptType === 'jumpcloud') {
        status = this.user.jumpcloud_status
      } else if (scriptType === 'google') {
        status = this.user.google_status
      } else if (scriptType === 'automox') {
        status = this.user.automox_status
      }
      
      return status || 'NOT RUN YET'
    },
    
    getScriptStatusClass(scriptType) {
      const status = this.getScriptStatusText(scriptType)
      
      if (status === 'NOT RUN YET') {
        return 'script-status-not-run'
      } else if (status.includes('TERMINATED') || status.includes('REMOVED')) {
        return 'script-status-success'
      } else if (status.includes('NOT FOUND')) {
        return 'script-status-warning'
      } else if (status.includes('FAILED')) {
        return 'script-status-error'
      } else {
        return 'script-status-unknown'
      }
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
        
        // Refresh user data to get updated script statuses
        await this.fetchUser()
        
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
  gap: 16px;
}

.script-group {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.script-group:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.script-header {
  margin-bottom: 16px;
}

.script-header h3 {
  margin: 0 0 8px 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge-container {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.status-label {
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 500;
  min-width: fit-content;
}

.status-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 16px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid;
  white-space: nowrap;
  transition: all 0.2s ease;
}

/* Script Status Badge Colors */
.script-status-not-run {
  background: #f3f4f6;
  color: #6b7280;
  border-color: #d1d5db;
}

.script-status-success {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
  border-color: #10b981;
  box-shadow: 0 1px 3px rgba(16, 185, 129, 0.2);
}

.script-status-warning {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border-color: #f59e0b;
  box-shadow: 0 1px 3px rgba(245, 158, 11, 0.2);
}

.script-status-error {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #991b1b;
  border-color: #ef4444;
  box-shadow: 0 1px 3px rgba(239, 68, 68, 0.2);
}

.script-status-unknown {
  background: #f3f4f6;
  color: #374151;
  border-color: #6b7280;
}

.script-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-start;
}
.btn-back {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: linear-gradient(135deg, #ac83b7 0%, #75797f 100%);
  color: #475569;
  border: 1px solid #e2e8f0;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  text-decoration: none;
  white-space: nowrap;
  height: 40px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.btn-back:hover {
  background: linear-gradient(135deg, #f1f5f9 0%, #cbd5e1 100%);
  border-color: #cbd5e1;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Button Styles */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: linear-gradient(135deg, #26adec 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 26px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  text-align: center;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-right: 8px;
  width: auto;
  max-width: 200px;
  height: 40px;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.btn-icon {
  font-size: 0.85rem;
  flex-shrink: 0;
}

.btn-text {
  font-weight: 500;
  color: white;
  margin-right: 4px;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: linear-gradient(135deg, #f8fafc 0%, #c6b9cb 100%);
  color: #475569;
  border: 1px solid #c3cad2;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  white-space: nowrap;
  height: 40px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #f1f5f9 0%, #cbd5e1 100%);
  border-color: #8e99a5;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
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

/* New detailed status classes */
.log-entry.log-success {
  border-left: 4px solid #10b981;
}

.log-entry.log-warning {
  border-left: 4px solid #f59e0b;
}

.log-entry.log-error {
  border-left: 4px solid #ef4444;
}

.log-entry.log-unknown {
  border-left: 4px solid #6b7280;
}

/* Status badges */
.status-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  min-width: 100px;
  text-align: center;
  white-space: nowrap;
}

.badge-success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #10b981;
}

.badge-warning {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #f59e0b;
}

.badge-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #ef4444;
}

.badge-unknown {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #6b7280;
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
  flex-wrap: wrap;
}

.status-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.script-name {
  font-weight: 600;
  color: #1f2937;
  text-transform: capitalize;
  min-width: 140px;
  flex-shrink: 0;
}

.time-text {
  color: #6b7280;
  font-size: 0.85rem;
  min-width: 120px;
  flex-shrink: 0;
}

.user-text {
  color: #6b7280;
  font-size: 0.85rem;
  min-width: 100px;
  flex-shrink: 0;
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

/* Loading Overlay Styles */
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
  min-width: 280px;
  animation: slideIn 0.3s ease-out;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.loading-content p {
  margin: 0 0 8px 0;
  color: #374151;
  font-weight: 600;
  font-size: 1rem;
}

.loading-details small {
  color: #6b7280;
  font-size: 0.85rem;
  font-style: italic;
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
</style>
