<template>
  <div class="settings-page">
    <div class="page-header">
      <div class="header-content">
        <h1><i class="fas fa-cog"></i> Admin Settings</h1>
        <p>Configure system settings and organizational preferences</p>
      </div>
    </div>

    <!-- Settings Navigation Cards -->
    <div class="settings-navigation">
      <!-- Department OU Mappings Card -->
      <div class="nav-card" :class="{ 'active': activeTile === 'departments' }" @click="setActiveTile('departments')">
        <div class="card-icon">
          <i class="fas fa-building"></i>
        </div>
        <div class="card-content">
          <h3>Department Mappings</h3>
          <p>Organizational unit configurations</p>
          <div class="card-meta">
            <span class="meta-badge">{{ departmentMappings.length }} departments</span>
          </div>
        </div>
      </div>

      <!-- User Settings Card -->
      <div class="nav-card" :class="{ 'active': activeTile === 'users' }" @click="setActiveTile('users')">
        <div class="card-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="card-content">
          <h3>User Management</h3>
          <p>Default settings and preferences</p>
          <div class="card-meta">
            <!-- <span class="meta-badge coming-soon">Coming Soon</span> -->
          </div>
        </div>
      </div>

      <!-- Sync Management Card -->
      <div class="nav-card" :class="{ 'active': activeTile === 'sync' }" @click="setActiveTile('sync')">
        <div class="card-icon">
          <i class="fas fa-sync-alt"></i>
        </div>
        <div class="card-content">
          <h3>Sync Management</h3>
          <p>Freshservice integration & automation</p>
          <div class="card-meta">
            <span class="meta-badge" :class="{ 'status-active': syncStatus.running, 'status-stopped': !syncStatus.running }">
              <i class="fas fa-circle"></i>
              {{ syncStatus.running ? 'Active' : 'Stopped' }}
            </span>
          </div>
        </div>
      </div>

      <!-- System Settings Card -->
      <div class="nav-card" :class="{ 'active': activeTile === 'system' }" @click="setActiveTile('system')">
        <div class="card-icon">
          <i class="fas fa-server"></i>
        </div>
        <div class="card-content">
          <h3>System Settings</h3>
          <p>Global configuration options</p>
          <div class="card-meta">
            <!-- <span class="meta-badge coming-soon">Coming Soon</span> -->
          </div>
        </div>
      </div>
    </div>

    <!-- Department OU Mappings Section -->
    <div v-if="activeTile === 'departments'" class="content-section">
      <div class="section-header">
        <div class="section-title">
          <i class="fas fa-building"></i>
          <h2>Department OU Mappings</h2>
        </div>
        <div class="header-actions">
          <button class="btn-outline" @click="addDepartment">
            <i class="fas fa-plus"></i> Add Department
          </button>
          <button class="btn-primary" @click="saveMappings">
            <i class="fas fa-save"></i> Save Changes
          </button>
        </div>
      </div>
      
      <div class="settings-content">
        <div class="search-filter">
          <div class="search-input-wrapper">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search departments..." 
              class="search-input"
            >
          </div>
          <button class="btn-secondary" @click="resetToDefaults">
            <i class="fas fa-undo"></i> Reset to Defaults
          </button>
        </div>
        
        <div class="department-list">
          <div class="list-header">
            <div class="col-department">Department Name</div>
            <div class="col-ou">Organizational Unit (OU)</div>
            <div class="col-actions">Actions</div>
          </div>
          
          <div 
            v-for="(mapping, index) in filteredMappings" 
            :key="index"
            class="department-row"
            :class="{ 'editing': mapping.isEditing }"
          >
            <div class="col-department">
              <input 
                v-if="mapping.isEditing"
                v-model="mapping.department"
                class="edit-input"
                @keyup.enter="saveMapping(index)"
                @keyup.escape="cancelEdit(index)"
              >
              <span v-else>{{ mapping.department }}</span>
            </div>
            
            <div class="col-ou">
              <input 
                v-if="mapping.isEditing"
                v-model="mapping.ou"
                class="edit-input"
                placeholder="/Department/Subdepartment"
                @keyup.enter="saveMapping(index)"
                @keyup.escape="cancelEdit(index)"
              >
              <code v-else class="ou-path">{{ mapping.ou }}</code>
            </div>
            
            <div class="col-actions">
              <div v-if="mapping.isEditing" class="edit-actions">
                <button class="btn-save" @click="saveMapping(index)" title="Save">
                  <i class="fas fa-check"></i>
                </button>
                <button class="btn-cancel" @click="cancelEdit(index)" title="Cancel">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <div v-else class="view-actions">
                <button class="btn-edit" @click="editMapping(index)" title="Edit">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn-delete" @click="deleteMapping(index)" title="Delete">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="filteredMappings.length === 0" class="no-results">
            <p>No departments found matching "{{ searchQuery }}"</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- System Information Section -->
    <div v-if="activeTile === 'departments'" class="content-section">
      <div class="section-header">
        <div class="section-title">
          <i class="fas fa-chart-bar"></i>
          <h2>System Information</h2>
        </div>
      </div>
      
      <div class="settings-content">
        <div class="info-grid">
          <div class="info-card">
            <div class="info-icon">
              <i class="fas fa-building"></i>
            </div>
            <div class="info-content">
              <h3>Total Departments</h3>
              <p class="info-value">{{ departmentMappings.length }}</p>
            </div>
          </div>
          
          <div class="info-card">
            <div class="info-icon">
              <i class="fas fa-sitemap"></i>
            </div>
            <div class="info-content">
              <h3>Active OUs</h3>
              <p class="info-value">{{ uniqueOUs.length }}</p>
            </div>
          </div>
          
          <div class="info-card">
            <div class="info-icon">
              <i class="fas fa-clock"></i>
            </div>
            <div class="info-content">
              <h3>Last Updated</h3>
              <p class="info-value">{{ lastUpdated }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Sync Management Section -->
    <div v-if="activeTile === 'sync'" class="content-section">
      <div class="section-header">
        <div class="section-title">
          <i class="fas fa-sync-alt"></i>
          <h2>Freshservice Sync Management</h2>
        </div>
        <div class="header-actions">
          <button 
            class="btn-outline" 
            @click="refreshSyncStatus"
            :disabled="isRefreshingStatus"
          >
            <i class="fas" :class="isRefreshingStatus ? 'fa-spinner fa-spin' : 'fa-refresh'"></i> 
            {{ isRefreshingStatus ? 'Refreshing...' : 'Refresh Status' }}
          </button>
          <button 
            class="btn-primary" 
            @click="triggerManualSync"
            :disabled="isManualSyncRunning"
          >
            <i class="fas" :class="isManualSyncRunning ? 'fa-spinner fa-spin' : 'fa-play'"></i>
            {{ isManualSyncRunning ? 'Syncing...' : 'Manual Sync' }}
          </button>
        </div>
      </div>
      
      <div class="settings-content">
        <!-- Sync Status Cards -->
        <div class="sync-status-grid">
          <div class="status-card">
            <div class="status-icon" :class="{ 'active': syncStatus.running, 'warning': syncStatus.failures > 0 }">
              <i class="fas" :class="syncStatus.running ? (syncStatus.failures > 0 ? 'fa-exclamation-triangle' : 'fa-check-circle') : 'fa-times-circle'"></i>
            </div>
            <div class="status-content">
              <h3>Automated Sync</h3>
              <p>{{ syncStatus.running ? 'Running every 5 min + hourly' : 'Currently stopped' }}</p>
              <small v-if="syncStatus.nextRun">Next run: {{ formatDateTime(syncStatus.nextRun) }}</small>
              <small v-if="syncStatus.failures > 0" class="warning-text">{{ syncStatus.failures }} consecutive failures</small>
            </div>
          </div>
          
          <div class="status-card">
            <div class="status-icon">
              <i class="fas fa-tasks"></i>
            </div>
            <div class="status-content">
              <h3>Scheduler Jobs</h3>
              <p>{{ syncStatus.totalJobs || 0 }} active tasks</p>
              <small>5min sync, hourly sync, heartbeat</small>
            </div>
          </div>
          
          <div class="status-card">
            <div class="status-icon">
              <i class="fas fa-clock"></i>
            </div>
            <div class="status-content">
              <h3>Last Successful Sync</h3>
              <p v-if="syncStatus.lastSuccess">{{ formatDateTime(syncStatus.lastSuccess) }}</p>
              <p v-else-if="syncStatus.lastAttempt">{{ formatDateTime(syncStatus.lastAttempt) }} (failed)</p>
              <p v-else>No sync attempts yet</p>
              <small v-if="syncStatus.lastSuccess">Automated sync working</small>
            </div>
          </div>
          
          <div class="status-card">
            <div class="status-icon">
              <i class="fas fa-hand-paper"></i>
            </div>
            <div class="status-content">
              <h3>Manual Sync</h3>
              <p v-if="lastManualSync.timestamp">{{ formatDateTime(lastManualSync.timestamp) }}</p>
              <p v-else>Never run manually</p>
              <small v-if="lastManualSync.result">{{ lastManualSync.result.users_created }} users created</small>
            </div>
          </div>
        </div>
        
        <!-- Manual Sync Results -->
        <div v-if="manualSyncResult" class="sync-result-card" :class="{ 'success': manualSyncResult.success, 'error': !manualSyncResult.success }">
          <div class="result-header">
            <h3>
              <i class="fas" :class="manualSyncResult.success ? 'fa-check-circle' : 'fa-exclamation-circle'"></i>
              {{ manualSyncResult.success ? 'Sync Completed' : 'Sync Failed' }}
            </h3>
            <button @click="manualSyncResult = null" class="close-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="result-content">
            <p>{{ manualSyncResult.message }}</p>
            <div v-if="manualSyncResult.result" class="sync-stats">
              <div class="stat">
                <span class="stat-label">Tickets Processed:</span>
                <span class="stat-value">{{ manualSyncResult.result.tickets_processed }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">Users Created:</span>
                <span class="stat-value">{{ manualSyncResult.result.users_created }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">Users Skipped:</span>
                <span class="stat-value">{{ manualSyncResult.result.users_skipped }}</span>
              </div>
            </div>
            <div v-if="manualSyncResult.result && manualSyncResult.result.processed_tickets" class="processed-tickets">
              <h4>Processed Tickets:</h4>
              <div class="ticket-list">
                <div 
                  v-for="ticket in manualSyncResult.result.processed_tickets" 
                  :key="ticket.ticket_id"
                  class="ticket-item"
                >
                  <span class="ticket-id">#{{ ticket.ticket_id }}</span>
                  <span class="ticket-user">{{ ticket.user_name }}</span>
                  <span class="ticket-email">{{ ticket.company_email }}</span>
                  <span class="ticket-dept">{{ ticket.department }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Sync Configuration
        <div class="config-section">
          <h3><i class="fas fa-cogs"></i> Sync Configuration</h3>
          <div class="config-grid">
            <div class="config-item">
              <label><i class="fas fa-clock"></i> Sync Frequency</label>
              <p>Every hour (automated)</p>
            </div>
            <div class="config-item">
              <label><i class="fas fa-filter"></i> Ticket Filter</label>
              <p>Subject starts with "NEW ONBOARDING"</p>
            </div>
            <div class="config-item">
              <label><i class="fas fa-calendar"></i> Time Window</label>
              <p>Last 24 hours</p>
            </div>
            <div class="config-item">
              <label><i class="fas fa-database"></i> Source System</label>
              <p>Freshservice API</p>
            </div>
          </div>
        </div> -->

        <!-- Sync Logs Section -->
        <div class="config-section">
          <div class="logs-header">
            <h3><i class="fas fa-list-alt"></i> Recent Sync Activity</h3>
            <div class="logs-actions">
              <span class="logs-subtitle">{{ syncLogs.length }} sync records</span>
              <button 
                class="btn-outline" 
                @click="fetchSyncLogs"
                :disabled="isRefreshingLogs"
              >
                <i class="fas" :class="isRefreshingLogs ? 'fa-spinner fa-spin' : 'fa-sync-alt'"></i> 
                {{ isRefreshingLogs ? 'Refreshing...' : 'Refresh Logs' }}
              </button>
            </div>
          </div>
          
          <div v-if="syncLogs.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="fas fa-clipboard-list"></i>
            </div>
            <p>No sync history available</p>
            <small>Automated syncs run hourly</small>
          </div>
          
          <!-- Scrollable logs container -->
          <div v-else class="sync-logs-container">
            <div class="logs-table-header">
              <div class="col-status">Status</div>
              <div class="col-time">Time</div>
              <div class="col-trigger">Trigger</div>
              <div class="col-metrics">Results</div>
              <div class="col-duration">Duration</div>
            </div>
            
            <div class="logs-table-body">
              <div v-for="(log, index) in syncLogs" :key="index" class="log-row-container">
                <div class="log-row" @click="toggleSyncLogExpanded(index)">
                  <div class="col-status">
                    <span class="status-badge" :class="log.status === 'success' ? 'success' : 'failed'">
                      <i class="fas" :class="log.status === 'success' ? 'fa-check-circle' : 'fa-times-circle'"></i>
                    </span>
                  </div>
                  
                  <div class="col-time">
                    <div class="time-display">
                      {{ formatDateTime(log.executed_at) }}
                    </div>
                  </div>
                  
                  <div class="col-trigger">
                    <span class="trigger-badge" :class="log.triggered_by === 'scheduler' ? 'auto' : 'manual'">
                      <i class="fas" :class="log.triggered_by === 'scheduler' ? 'fa-robot' : 'fa-user'"></i>
                      {{ log.triggered_by === 'scheduler' ? ' Auto' : ' Manual' }}
                    </span>
                  </div>
                  
                  <div class="col-metrics">
                    <div class="metrics-display">
                      <span v-if="log.tickets_processed">{{ log.tickets_processed }} tickets</span>
                      <span v-if="log.users_created">{{ log.users_created }} users</span>
                      <span v-if="log.users_skipped">{{ log.users_skipped }} skipped</span>
                    </div>
                  </div>
                  
                  <div class="col-duration">
                    <div class="duration-expand">
                      <span v-if="log.execution_time">{{ log.execution_time }}s</span>
                      <span v-else>—</span>
                      <i class="fas fa-chevron-down expand-icon" :class="{ 'expanded': log.expanded }"></i>
                    </div>
                  </div>
                </div>
                
                <!-- Detailed execution logs -->
                <div v-if="log.expanded" class="log-details">
                  <div class="log-details-header">
                    <h4><i class="fas fa-list-alt"></i> Detailed Execution Log</h4>
                    <small>Log ID: {{ log.log_id }}</small>
                  </div>
                  <div class="log-output">
                    <pre v-if="log.output">{{ log.output }}</pre>
                    <p v-else class="no-details">No detailed execution log available for this sync.</p>
                    
                    <div v-if="log.error" class="log-error">
                      <h5><i class="fas fa-exclamation-triangle"></i> Error Details</h5>
                      <pre>{{ log.error }}</pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Placeholder for other settings tiles -->
    <div v-if="activeTile !== 'departments' && activeTile !== 'sync'" class="content-section">
      <div class="section-header">
        <div class="section-title">
          <i class="fas fa-tools"></i>
          <h2>{{ getActiveTileTitle() }}</h2>
        </div>
      </div>
      
      <div class="settings-content">
        <div class="coming-soon">
          <div class="coming-soon-icon">
            <i class="fas fa-hammer"></i>
          </div>
          <h3>Coming Soon</h3>
          <p>This settings section is currently under development and will be available in a future update.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useDepartmentMappings } from '@/composables/useDepartmentMappings'

export default {
  name: 'SettingsView',
  setup() {
    const {
      departmentMappings,
      getDepartmentOU,
      updateMappings,
      addMapping,
      removeMapping,
      resetToDefaults: resetMappingsToDefaults
    } = useDepartmentMappings()

    return {
      departmentMappings,
      getDepartmentOU,
      updateMappings,
      addMapping,
      removeMapping,
      resetMappingsToDefaults
    }
  },
  data() {
    return {
      activeTile: 'departments', // Default to departments tile
      searchQuery: '',
      lastUpdated: new Date().toLocaleDateString(),
      // Sync Management Data
      syncStatus: {
        running: false,
        nextRun: null,
        totalJobs: 0
      },
      isManualSyncRunning: false,
      isRefreshingStatus: false,
      isRefreshingLogs: false,
      manualSyncResult: null,
      lastManualSync: {
        timestamp: null,
        result: null
      },
      syncLogs: [] // Initialize as empty array to prevent undefined errors
    }
  },
  computed: {
    filteredMappings() {
      if (!this.searchQuery) {
        return this.departmentMappings
      }
      return this.departmentMappings.filter(mapping => 
        mapping.department.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        mapping.ou.toLowerCase().includes(this.searchQuery.toLowerCase())
      )
    },
    uniqueOUs() {
      const ous = this.departmentMappings.map(mapping => mapping.ou)
      return [...new Set(ous)]
    }
  },
  methods: {
    setActiveTile(tile) {
      this.activeTile = tile
      
      // If switching to sync tile and syncLogs is not loaded, fetch them
      if (tile === 'sync' && (!this.syncLogs || this.syncLogs.length === 0)) {
        this.fetchSyncLogs()
      }
    },
    
    getActiveTileTitle() {
      const titles = {
        users: 'User Settings',
        sync: 'Sync Management',
        system: 'System Settings'
      }
      return titles[this.activeTile] || 'Settings'
    },
    
    addDepartment() {
      const newMapping = {
        department: 'NEW DEPARTMENT',
        ou: '/New Department',
        isEditing: true,
        originalData: null
      }
      this.departmentMappings.unshift(newMapping)
      this.searchQuery = '' // Clear search to show new department
    },
    
    editMapping(index) {
      const mapping = this.filteredMappings[index]
      const originalIndex = this.departmentMappings.findIndex(m => m === mapping)
      
      // Store original data for cancel functionality
      this.departmentMappings[originalIndex].originalData = {
        department: mapping.department,
        ou: mapping.ou
      }
      this.departmentMappings[originalIndex].isEditing = true
    },
    
    saveMapping(index) {
      const mapping = this.filteredMappings[index]
      const originalIndex = this.departmentMappings.findIndex(m => m === mapping)
      
      // Validate input
      if (!mapping.department.trim() || !mapping.ou.trim()) {
        alert('Both department name and OU are required')
        return
      }
      
      this.departmentMappings[originalIndex].isEditing = false
      this.departmentMappings[originalIndex].originalData = null
      this.lastUpdated = new Date().toLocaleDateString()
    },
    
    cancelEdit(index) {
      const mapping = this.filteredMappings[index]
      const originalIndex = this.departmentMappings.findIndex(m => m === mapping)
      
      if (mapping.originalData) {
        // Restore original data
        this.departmentMappings[originalIndex].department = mapping.originalData.department
        this.departmentMappings[originalIndex].ou = mapping.originalData.ou
        this.departmentMappings[originalIndex].originalData = null
      } else {
        // Remove if it was a new department
        this.departmentMappings.splice(originalIndex, 1)
      }
      this.departmentMappings[originalIndex].isEditing = false
    },
    
    deleteMapping(index) {
      const mapping = this.filteredMappings[index]
      const originalIndex = this.departmentMappings.findIndex(m => m === mapping)
      
      if (confirm(`Are you sure you want to delete the department "${mapping.department}"?`)) {
        this.departmentMappings.splice(originalIndex, 1)
        this.lastUpdated = new Date().toLocaleDateString()
      }
    },
    
    saveMappings() {
      // Here you would typically save to backend/database
      console.log('Saving department mappings:', this.departmentMappings)
      this.lastUpdated = new Date().toLocaleDateString()
      alert('Department mappings saved successfully!')
    },
    
    resetToDefaults() {
      if (confirm('Are you sure you want to reset all department mappings to defaults? This will lose any custom changes.')) {
        this.resetMappingsToDefaults()
        this.lastUpdated = new Date().toLocaleDateString()
      }
    },
    
    // Sync Management Methods
    async refreshSyncStatus() {
      if (this.isRefreshingStatus) return
      
      this.isRefreshingStatus = true
      try {
        const response = await fetch('/api/v1/dashboard/scheduler-status')
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        const data = await response.json()
        
        if (data.success && data.status) {
          this.syncStatus = {
            running: data.status.running || false,
            nextRun: data.status.next_sync_time || null,
            totalJobs: data.status.jobs_count || 0,
            lastAttempt: data.status.last_sync_attempt || null,
            lastSuccess: data.status.last_sync_success || null,
            failures: data.status.consecutive_failures || 0
          }
          
          // Update lastManualSync from API if available
          if (data.status.last_manual_sync) {
            this.lastManualSync = {
              timestamp: data.status.last_manual_sync.timestamp || null,
              result: data.status.last_manual_sync.result || null
            }
          }
        } else {
          console.warn('Scheduler status unavailable:', data)
          this.syncStatus = {
            running: false,
            nextRun: null,
            totalJobs: 0,
            lastAttempt: null,
            lastSuccess: null,
            failures: 0
          }
        }
      } catch (error) {
        console.error('Error fetching sync status:', error)
        this.syncStatus = {
          running: false,
          nextRun: null,
          totalJobs: 0,
          lastAttempt: null,
          lastSuccess: null,
          failures: 0
        }
      } finally {
        this.isRefreshingStatus = false
      }
    },
    
    async triggerManualSync() {
      if (this.isManualSyncRunning) return
      
      this.isManualSyncRunning = true
      this.manualSyncResult = null
      
      try {
        const response = await fetch('/api/v1/admin/sync/freshservice/manual', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        
        const data = await response.json()
        
        this.manualSyncResult = data
        
        if (data.success) {
          this.lastManualSync = {
            timestamp: new Date().toISOString(),
            result: data.result
          }
          
          // Refresh logs to show the new manual sync
          await this.fetchSyncLogs()
        }
        
        // Refresh sync status after manual sync
        await this.refreshSyncStatus()
        
      } catch (error) {
        console.error('Error triggering manual sync:', error)
        this.manualSyncResult = {
          success: false,
          message: 'Failed to trigger manual sync: ' + error.message
        }
      } finally {
        this.isManualSyncRunning = false
      }
    },
    
    formatDateTime(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },

    formatTime(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      const today = new Date()
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)
      
      if (date.toDateString() === today.toDateString()) {
        return 'Today'
      } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday'
      } else {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
      }
    },

    async fetchSyncLogs() {
      if (this.isRefreshingLogs) return
      
      this.isRefreshingLogs = true
      try {
        // Fetch from dedicated sync_logs table
        const response = await fetch('/api/v1/admin/sync/logs?limit=50')
        if (response.ok) {
          const data = await response.json()
          console.log('Sync logs API response:', data)
          
          if (data.success && data.logs) {
            // Transform to frontend format
            this.syncLogs = data.logs.map((log) => ({
              success: log.status === 'success',
              sync_type: log.sync_source || 'Freshservice Onboarding Sync',
              executed_at: log.started_at || new Date().toISOString(),
              executed_by: log.triggered_by || 'Unknown',
              execution_time: log.execution_time_seconds || null,
              output: log.output_message || '',
              error: log.error_message || '',
              expanded: false,
              log_id: log.id,
              status: log.status,
              tickets_processed: log.tickets_processed || 0,
              users_created: log.users_created || 0,
              users_skipped: log.users_skipped || 0,
              triggered_by: log.triggered_by === 'automated_scheduler' ? 'scheduler' : 'manual'
            }))
            
            // Find the most recent manual sync to populate lastManualSync
            const manualSyncs = this.syncLogs.filter(log => log.triggered_by === 'manual')
            if (manualSyncs.length > 0) {
              const lastManual = manualSyncs[0] // Already sorted by most recent
              this.lastManualSync = {
                timestamp: lastManual.executed_at,
                result: {
                  users_created: lastManual.users_created,
                  tickets_processed: lastManual.tickets_processed,
                  users_skipped: lastManual.users_skipped
                }
              }
            }
            
            console.log('Sync logs loaded successfully:', this.syncLogs.length, 'records')
          } else {
            console.error('API returned no logs or error:', data)
            this.syncLogs = []
          }
        } else {
          console.error('Failed to fetch sync logs - HTTP status:', response.status)
          this.syncLogs = []
        }
      } catch (error) {
        console.error('Error fetching sync logs:', error)
        this.syncLogs = []
      } finally {
        this.isRefreshingLogs = false
      }
    },

    toggleSyncLogExpanded(index) {
      // Safety check to ensure the log exists and has the expanded property
      if (this.syncLogs && this.syncLogs[index] && typeof this.syncLogs[index].expanded !== 'undefined') {
        this.syncLogs[index].expanded = !this.syncLogs[index].expanded
      } else {
        console.warn(`Cannot toggle sync log at index ${index}: log or expanded property not found`)
      }
    }
  },
  
  async mounted() {
    // Load sync status when component mounts
    await this.refreshSyncStatus()
    await this.fetchSyncLogs()
  }
}
</script>

<style scoped>
.settings-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px;
  background: #f8fafc;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
  background: linear-gradient(135deg,  #d8f0ff 0%, #454a62 100%);
  border-radius: 12px;
  padding: 10px 24px;
  color: rgb(50, 49, 49);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.header-content h1 {
  margin: 0 0 6px 0;
  font-size: 1.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-content h1 i {
  font-size: 1.5rem;
  opacity: 0.9;
}

.header-content p {
  margin: 0;
  font-size: 0.7rem;
  opacity: 0.9;
  font-weight: 200;
}

/* Modern Navigation Cards */
.settings-navigation {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.nav-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 80px;
}

.nav-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.nav-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.nav-card:hover::before {
  transform: scaleX(1);
}

.nav-card.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
}

.nav-card.active::before {
  transform: scaleX(1);
}

.card-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.card-icon i {
  font-size: 1.1rem;
  color: white;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-content h3 {
  margin: 0 0 4px 0;
  color: #1a202c;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.2;
}

.card-content p {
  margin: 0 0 8px 0;
  color: #718096;
  font-size: 0.8rem;
  line-height: 1.3;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #667eea;
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

.meta-badge.coming-soon {
  background: #a0aec0;
}

.meta-badge.status-active {
  background: #48bb78;
}

.meta-badge.status-active i {
  animation: pulse 2s infinite;
}

.meta-badge.status-stopped {
  background: #f56565;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Content Sections */
.content-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  margin-bottom: 16px;
  border: 1px solid #e2e8f0;
}

.section-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-title i {
  font-size: 1.2rem;
  color: #667eea;
}

.section-title h2 {
  margin: 0;
  color: #1a202c;
  font-size: 1.2rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.settings-content {
  padding: 20px;
}

/* Search Filter */
.search-filter {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
}

.search-input-wrapper i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #a0aec0;
  font-size: 0.85rem;
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 36px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  background: white;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Modern Buttons */
.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-outline {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.btn-outline:hover {
  background: #667eea;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: #edf2f7;
  color: #4a5568;
  border: 2px solid #e2e8f0;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e0;
  transform: translateY(-1px);
}

/* Department List Styling */
.department-list {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.list-header {
  display: grid;
  grid-template-columns: 1fr 2fr 120px;
  gap: 16px;
  padding: 12px 16px;
  background: #f7fafc;
  border-bottom: 2px solid #e2e8f0;
  font-weight: 600;
  color: #4a5568;
  font-size: 0.85rem;
}

.department-row {
  display: grid;
  grid-template-columns: 1fr 2fr 120px;
  gap: 16px;
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  align-items: center;
  transition: background-color 0.2s ease;
}

.department-row:hover {
  background: #f8fafc;
}

.department-row.editing {
  background: #eef6ff;
  border-color: #bee3f8;
}

.department-row:last-child {
  border-bottom: none;
}

.col-department {
  font-weight: 600;
  color: #1a202c;
  font-size: 0.9rem;
}

.ou-path {
  background: #edf2f7;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #4a5568;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.edit-input {
  width: 100%;
  padding: 8px 10px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.85rem;
  transition: border-color 0.3s ease;
}

.edit-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Action Buttons */
.col-actions {
  display: flex;
  justify-content: flex-end;
}

.edit-actions,
.view-actions {
  display: flex;
  gap: 8px;
}

.btn-edit,
.btn-delete,
.btn-save,
.btn-cancel {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-edit {
  color: #667eea;
  background: #eef6ff;
}

.btn-edit:hover {
  background: #bee3f8;
}

.btn-delete {
  color: #f56565;
  background: #fed7d7;
}

.btn-delete:hover {
  background: #feb2b2;
}

.btn-save {
  color: #48bb78;
  background: #c6f6d5;
}

.btn-save:hover {
  background: #9ae6b4;
}

.btn-cancel {
  color: #f56565;
  background: #fed7d7;
}

.btn-cancel:hover {
  background: #feb2b2;
}

/* Info Cards */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-card {
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.info-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.1rem;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.info-content h3 {
  margin: 0 0 2px 0;
  color: #4a5568;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  margin: 0;
  color: #1a202c;
  font-size: 1.4rem;
  font-weight: 700;
}

/* Sync Status Cards */
.sync-status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.status-card {
  background: rgb(219, 219, 219);
  border: 1px solid #accefb;
  border-radius: 10px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.status-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.status-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  color: #64748b;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.status-icon.active {
  background: #dcfce7;
  color: #16a34a;
}

.status-icon.warning {
  background: #fef3c7;
  color: #d97706;
}

.status-content h3 {
  margin: 0 0 3px 0;
  color: #1a202c;
  font-size: 0.95rem;
  font-weight: 600;
}

.status-content p {
  margin: 0 0 3px 0;
  color: #64748b;
  font-size: 0.8rem;
}

.status-content small {
  color: #94a3b8;
  font-size: 0.75rem;
}

.status-content small.warning-text {
  color: #d97706;
  font-weight: 500;
}

/* Sync Result Card */
.sync-result-card {
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 32px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.sync-result-card.success {
  background: linear-gradient(135deg, #f0fff4 0%, #dcfce7 100%);
  border-color: #16a34a;
}

.sync-result-card.error {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-color: #dc2626;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.result-header h3 {
  margin: 0;
  color: #1a202c;
  font-size: 1.2rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #64748b;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: #1a202c;
  background: rgba(0, 0, 0, 0.05);
}

/* Config Section */
.config-section {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.config-section h3 {
  margin: 0 0 16px 0;
  color: #1a202c;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-section h3 i {
  color: #667eea;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px;
  background: #e0eefc;
  border-radius: 8px;
  border: 1px solid #cfcfcf;
}

.config-item label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #4a5568;
  display: flex;
  align-items: center;
  gap: 6px;
}

.config-item label i {
  color: #667eea;
}

.config-item p {
  margin: 0;
  color: #1a202c;
  font-size: 0.85rem;
  font-weight: 500;
}

/* Logs Styling */
.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.logs-header h3 {
  margin: 0;
  color: #1a202c;
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.logs-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logs-subtitle {
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 32px 20px;
  background: #f8fafc;
  border-radius: 8px;
  border: 2px dashed #cbd5e0;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
  color: #94a3b8;
}

.empty-state p {
  margin: 0 0 6px 0;
  color: #4a5568;
  font-weight: 500;
  font-size: 1rem;
}

.empty-state small {
  color: #64748b;
  font-size: 0.85rem;
}

/* Sync Logs Container */
.sync-logs-container {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  overflow: hidden;
  margin-top: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.logs-table-header {
  display: grid;
  grid-template-columns: 100px 160px 120px 180px 80px;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-bottom: 2px solid #e2e8f0;
  font-weight: 600;
  color: #4a5568;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.logs-table-header > div {
  padding: 12px 16px;
  display: flex;
  align-items: center;
}

.logs-table-body {
  max-height: 400px;
  overflow-y: auto;
}

.log-row {
  display: grid;
  grid-template-columns: 100px 160px 120px 180px 80px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.8rem;
  transition: background-color 0.2s ease;
}

.log-row:hover {
  background-color: #f8fafc;
}

.log-row:last-child {
  border-bottom: none;
}

.log-row > div {
  padding: 12px 16px;
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.status-badge.success {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.failed {
  background: #fee2e2;
  color: #dc2626;
}

.time-display {
  font-size: 0.8rem;
  color: #4a5568;
  font-weight: 500;
}

.trigger-badge {
  padding: 4px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.trigger-badge.auto {
  background: #dbeafe;
  color: #1d4ed8;
}

.trigger-badge.manual {
  background: #fed7aa;
  color: #ea580c;
}

.metrics-display {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.75rem;
  color: #64748b;
}

.metrics-display span {
  display: block;
  font-weight: 500;
}

/* Log Row Container for expandable logs */
.log-row-container {
  border-bottom: 1px solid #f1f5f9;
}

.log-row-container:last-child {
  border-bottom: none;
}

.log-row {
  display: grid;
  grid-template-columns: 100px 160px 120px 180px 80px;
  font-size: 0.8rem;
  transition: background-color 0.2s ease;
  cursor: pointer;
}

.log-row:hover {
  background-color: #f8fafc;
}

.duration-expand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.expand-icon {
  font-size: 0.7rem;
  color: #64748b;
  transition: transform 0.3s ease;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

/* Log Details (Expanded View) */
.log-details {
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  padding: 16px 20px;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
    padding-top: 0;
    padding-bottom: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
    padding-top: 16px;
    padding-bottom: 16px;
  }
}

.log-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}

.log-details-header h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1a202c;
  display: flex;
  align-items: center;
  gap: 6px;
}

.log-details-header small {
  color: #64748b;
  font-size: 0.75rem;
}

.log-output {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.log-output pre {
  margin: 0;
  font-size: 0.75rem;
  line-height: 1.5;
  color: #374151;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
}

.log-output .no-details {
  margin: 0;
  color: #64748b;
  font-style: italic;
  font-family: inherit;
  font-size: 0.8rem;
}

.log-error {
  margin-top: 12px;
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
}

.log-error h5 {
  margin: 0 0 8px 0;
  font-size: 0.8rem;
  color: #dc2626;
  display: flex;
  align-items: center;
  gap: 6px;
}

.log-error pre {
  margin: 0;
  font-size: 0.75rem;
  color: #b91c1c;
  background: white;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #f87171;
}

/* Coming Soon */
.coming-soon {
  text-align: center;
  padding: 48px 32px;
  color: #64748b;
}

.coming-soon-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  color: #94a3b8;
}

.coming-soon h3 {
  margin: 0 0 12px 0;
  color: #1a202c;
  font-size: 1.4rem;
  font-weight: 600;
}

.coming-soon p {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.6;
  max-width: 400px;
  margin: 0 auto;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .settings-navigation {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .settings-page {
    padding: 12px;
  }
  
  .settings-navigation {
    grid-template-columns: 1fr;
  }
  
  .nav-card {
    min-height: 70px;
    padding: 12px;
  }
  
  .card-icon {
    width: 36px;
    height: 36px;
  }
  
  .card-content h3 {
    font-size: 0.9rem;
  }
  
  .card-content p {
    font-size: 0.75rem;
  }
  
  .page-header {
    padding: 16px 20px;
  }
  
  .header-content h1 {
    font-size: 1.5rem;
  }
  
  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .search-filter {
    flex-direction: column;
    align-items: stretch;
  }
  
  .list-header,
  .department-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .col-actions {
    justify-content: flex-start;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .sync-status-grid {
    grid-template-columns: 1fr;
  }
  
  .config-grid {
    grid-template-columns: 1fr;
  }
  
  .logs-table-header,
  .log-row {
    grid-template-columns: 80px 120px 100px 140px 60px;
    font-size: 0.75rem;
  }
  
  .logs-table-header > div,
  .log-row > div {
    padding: 8px 12px;
  }
}

@media (max-width: 480px) {
  .logs-table-header,
  .log-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
  
  .logs-table-header > div,
  .log-row > div {
    padding: 6px 12px;
    border-bottom: 1px solid #f1f5f9;
  }
  
  .logs-table-header > div:last-child,
  .log-row > div:last-child {
    border-bottom: none;
  }
}
</style>
