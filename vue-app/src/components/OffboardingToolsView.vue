<template>
  <div class="offboarding-tools-page">
    <div class="page-header">
      <h1>Offboarding Tools</h1>
      <p>Run offboarding scripts and manage user deactivation</p>
    </div>

    <div v-if="user" class="user-info-section">
      <div class="user-card">
        <div class="user-details">
          <h2>{{ user.first_name }} {{ user.last_name }}</h2>
          <p class="user-email">{{ user.company_email }}</p>
          <p class="user-hostname" v-if="user.hostname">Hostname: {{ user.hostname }}</p>
          <p class="user-requested">Requested by: {{ user.requested_by }}</p>
          <p class="user-status">
            Status: <span :class="getStatusClass(user.status)">{{ user.status }}</span>
          </p>
        </div>
      </div>
    </div>

    <div class="scripts-section">
      <div class="content-section">
        <div class="section-header">
          <h2>Available Scripts</h2>
        </div>
        
        <div class="scripts-grid">
          <div class="script-card">
            <div class="script-header">
              <h3>JumpCloud User Deactivation</h3>
              <span class="script-type">jumpcloud</span>
            </div>
            <p class="script-description">Deactivate user account in JumpCloud directory</p>
            <button 
              class="btn-script"
              @click="executeScript('jumpcloud', 'deactivate_user')"
              :disabled="isRunning"
            >
              <i class="fa-solid fa-user-slash"></i>
              {{ isRunning ? 'Running...' : 'Deactivate User' }}
            </button>
          </div>

          <div class="script-card">
            <div class="script-header">
              <h3>Google Workspace Deactivation</h3>
              <span class="script-type">google</span>
            </div>
            <p class="script-description">Suspend user and transfer ownership in Google Workspace</p>
            <button 
              class="btn-script"
              @click="executeScript('google_workspace', 'deactivate_user')"
              :disabled="isRunning"
            >
              <i class="fa-brands fa-google"></i>
              {{ isRunning ? 'Running...' : 'Deactivate User' }}
            </button>
          </div>

          <div class="script-card">
            <div class="script-header">
              <h3>Equipment Collection</h3>
              <span class="script-type">system</span>
            </div>
            <p class="script-description">Generate equipment collection checklist and tracking</p>
            <button 
              class="btn-script"
              @click="executeScript('system', 'equipment_collection')"
              :disabled="isRunning"
            >
              <i class="fa-solid fa-laptop"></i>
              {{ isRunning ? 'Running...' : 'Generate Checklist' }}
            </button>
          </div>

          <div class="script-card">
            <div class="script-header">
              <h3>Access Review</h3>
              <span class="script-type">audit</span>
            </div>
            <p class="script-description">Review and document all user access permissions</p>
            <button 
              class="btn-script"
              @click="executeScript('audit', 'access_review')"
              :disabled="isRunning"
            >
              <i class="fa-solid fa-shield-halved"></i>
              {{ isRunning ? 'Running...' : 'Run Access Review' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Script Output Section -->
    <div v-if="lastExecution" class="output-section">
      <div class="content-section">
        <div class="section-header">
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

    <!-- Script Logs Section -->
    <div class="logs-section">
      <div class="content-section">
        <div class="section-header">
          <h2>Recent Script Logs</h2>
          <button class="btn-secondary" @click="fetchScriptLogs">
            <i class="fa-solid fa-arrows-rotate"></i> Refresh
          </button>
        </div>
        
        <div v-if="loadingLogs" class="loading-state">
          <p>Loading script logs...</p>
        </div>
        
        <div v-else-if="scriptLogs.length === 0" class="empty-state">
          <p>No script logs found for this user.</p>
        </div>
        
        <div v-else class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Script</th>
                <th>Status</th>
                <th>Executed By</th>
                <th>Started At</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in scriptLogs" :key="log.id">
                <td>{{ log.script_name }}</td>
                <td>
                  <span :class="getStatusClass(log.status)">{{ log.status }}</span>
                </td>
                <td>{{ log.executed_by }}</td>
                <td>{{ formatDate(log.started_at) }}</td>
                <td>{{ log.execution_time_seconds ? log.execution_time_seconds + 's' : 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'OffboardingToolsView',
  props: {
    userId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      user: null,
      isRunning: false,
      lastExecution: null,
      scriptLogs: [],
      loadingLogs: false,
      error: null
    }
  },
  mounted() {
    this.fetchUser()
    this.fetchScriptLogs()
  },
  methods: {
    async fetchUser() {
      try {
        const response = await axios.get(`/api/v1/offboarding/${this.userId}`)
        this.user = response.data
      } catch (error) {
        console.error('Error fetching user:', error)
        this.error = 'Failed to load user information'
      }
    },
    async fetchScriptLogs() {
      this.loadingLogs = true
      try {
        const response = await axios.get(`/api/v1/scripts/logs/user/${this.userId}`)
        this.scriptLogs = response.data
      } catch (error) {
        console.error('Error fetching script logs:', error)
      } finally {
        this.loadingLogs = false
      }
    },
    async executeScript(scriptType, scriptName) {
      this.isRunning = true
      try {
        const response = await axios.post('/api/v1/scripts/execute', {
          script_type: scriptType,
          script_name: scriptName,
          user_id: this.userId,
          additional_params: {
            offboarding_id: this.userId
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
        this.isRunning = false
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
    }
  }
}
</script>

<style scoped>
.offboarding-tools-page {
  padding: 0;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
}

.user-info-section {
  margin-bottom: 30px;
}

.user-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.user-details h2 {
  margin: 0 0 8px 0;
  color: #1f2937;
  font-size: 1.5rem;
}

.user-email {
  color: #667eea;
  font-weight: 500;
  margin: 4px 0;
}

.user-hostname,
.user-requested {
  color: #6b7280;
  margin: 4px 0;
}

.user-status {
  margin: 8px 0 0 0;
}

.content-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 30px;
}

.section-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.3rem;
}

.scripts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.script-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.script-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.script-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 12px;
}

.script-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.1rem;
}

.script-type {
  background: #f3f4f6;
  color: #6b7280;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  text-transform: uppercase;
  font-weight: 500;
}

.script-description {
  color: #6b7280;
  margin: 0 0 16px 0;
  line-height: 1.4;
}

.btn-script {
  width: 100%;
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-script:hover:not(:disabled) {
  background: #5a67d8;
}

.btn-script:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 1px solid #667eea;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
}

.output-section,
.logs-section {
  margin-bottom: 30px;
}

.execution-success {
  background: #f0fdf4;
  color: #16a34a;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.execution-failed {
  background: #fef2f2;
  color: #dc2626;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.output-content {
  padding: 20px;
}

.execution-info {
  background: #f9fafb;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 16px;
}

.execution-info p {
  margin: 4px 0;
  color: #6b7280;
}

.output-text pre {
  background: #1f2937;
  color: #f9fafb;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.4;
}

.error-text {
  margin-top: 16px;
}

.error-text h4 {
  color: #dc2626;
  margin: 0 0 8px 0;
}

.error-text pre {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.status-pending {
  background: #fef3c7;
  color: #d97706;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-in-progress {
  background: #dbeafe;
  color: #2563eb;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-completed {
  background: #f0fdf4;
  color: #16a34a;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-failed {
  background: #fef2f2;
  color: #dc2626;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.loading-state,
.empty-state {
  padding: 40px;
  text-align: center;
  color: #6b7280;
}

.table-container {
  padding: 0 20px 20px 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table tr:hover {
  background: #f9fafb;
}
</style>
