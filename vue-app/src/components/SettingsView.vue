<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>Admin Settings</h1>
      <p>Configure system settings and organizational preferences</p>
    </div>

    <!-- Settings Tiles Grid -->
    <div class="settings-tiles">
      <!-- Department OU Mappings Tile -->
      <div class="settings-tile" :class="{ 'active': activeTile === 'departments' }" @click="setActiveTile('departments')">
        <div class="tile-icon">🏢</div>
        <div class="tile-content">
          <h3>Department OU Mappings</h3>
          <p>Manage department to organizational unit mappings</p>
          <span class="tile-count">{{ departmentMappings.length }} departments</span>
        </div>
      </div>

      <!-- User Settings Tile -->
      <div class="settings-tile" :class="{ 'active': activeTile === 'users' }" @click="setActiveTile('users')">
        <div class="tile-icon">👥</div>
        <div class="tile-content">
          <h3>User Settings</h3>
          <p>Configure default user settings and preferences</p>
          <span class="tile-count">Coming Soon</span>
        </div>
      </div>

      <!-- Sync Management Tile -->
      <div class="settings-tile" :class="{ 'active': activeTile === 'sync' }" @click="setActiveTile('sync')">
        <div class="tile-icon">�</div>
        <div class="tile-content">
          <h3>Sync Management</h3>
          <p>Manage Freshservice onboarding sync and automation</p>
          <span class="tile-count" :class="{ 'sync-active': syncStatus.running }">
            {{ syncStatus.running ? 'Active' : 'Stopped' }}
          </span>
        </div>
      </div>

      <!-- System Settings Tile -->
      <div class="settings-tile" :class="{ 'active': activeTile === 'system' }" @click="setActiveTile('system')">
        <div class="tile-icon">⚙️</div>
        <div class="tile-content">
          <h3>System Settings</h3>
          <p>Configure system-wide settings and preferences</p>
          <span class="tile-count">Coming Soon</span>
        </div>
      </div>
    </div>

    <!-- Department OU Mappings Section -->
    <div v-if="activeTile === 'departments'" class="content-section">
      <div class="section-header">
        <h2>Department OU Mappings</h2>
        <div class="header-actions">
          <button class="btn-outline" @click="addDepartment">➕ Add Department</button>
          <button class="btn-primary" @click="saveMappings">💾 Save Changes</button>
        </div>
      </div>
      
      <div class="settings-content">
        <div class="search-filter">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search departments..." 
            class="search-input"
          >
          <button class="btn-secondary" @click="resetToDefaults">🔄 Reset to Defaults</button>
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
                <button class="btn-save" @click="saveMapping(index)" title="Save">✅</button>
                <button class="btn-cancel" @click="cancelEdit(index)" title="Cancel">❌</button>
              </div>
              <div v-else class="view-actions">
                <button class="btn-edit" @click="editMapping(index)" title="Edit">✏️</button>
                <button class="btn-delete" @click="deleteMapping(index)" title="Delete">🗑️</button>
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
        <h2>System Information</h2>
      </div>
      
      <div class="settings-content">
        <div class="info-grid">
          <div class="info-card">
            <div class="info-icon">📊</div>
            <div class="info-content">
              <h3>Total Departments</h3>
              <p class="info-value">{{ departmentMappings.length }}</p>
            </div>
          </div>
          
          <div class="info-card">
            <div class="info-icon">🏢</div>
            <div class="info-content">
              <h3>Active OUs</h3>
              <p class="info-value">{{ uniqueOUs.length }}</p>
            </div>
          </div>
          
          <div class="info-card">
            <div class="info-icon">⚙️</div>
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
        <h2>Freshservice Sync Management</h2>
        <div class="header-actions">
          <button class="btn-outline" @click="refreshSyncStatus">🔄 Refresh Status</button>
          <button 
            class="btn-primary" 
            @click="triggerManualSync"
            :disabled="isManualSyncRunning"
          >
            {{ isManualSyncRunning ? '⏳ Syncing...' : '🚀 Manual Sync' }}
          </button>
        </div>
      </div>
      
      <div class="settings-content">
        <!-- Sync Status Cards -->
        <div class="sync-status-grid">
          <div class="status-card">
            <div class="status-icon" :class="{ 'active': syncStatus.running }">
              {{ syncStatus.running ? '🟢' : '🔴' }}
            </div>
            <div class="status-content">
              <h3>Automated Sync</h3>
              <p>{{ syncStatus.running ? 'Running every hour' : 'Currently stopped' }}</p>
              <small v-if="syncStatus.nextRun">Next run: {{ formatDateTime(syncStatus.nextRun) }}</small>
            </div>
          </div>
          
          <div class="status-card">
            <div class="status-icon">📊</div>
            <div class="status-content">
              <h3>Total Jobs</h3>
              <p>{{ syncStatus.totalJobs || 0 }} scheduled tasks</p>
              <small>Background processes</small>
            </div>
          </div>
          
          <div class="status-card">
            <div class="status-icon">⏰</div>
            <div class="status-content">
              <h3>Last Manual Sync</h3>
              <p v-if="lastManualSync.timestamp">{{ formatDateTime(lastManualSync.timestamp) }}</p>
              <p v-else>Never run</p>
              <small v-if="lastManualSync.result">{{ lastManualSync.result.users_created }} users created</small>
            </div>
          </div>
        </div>
        
        <!-- Manual Sync Results -->
        <div v-if="manualSyncResult" class="sync-result-card" :class="{ 'success': manualSyncResult.success, 'error': !manualSyncResult.success }">
          <div class="result-header">
            <h3>{{ manualSyncResult.success ? '✅ Sync Completed' : '❌ Sync Failed' }}</h3>
            <button @click="manualSyncResult = null" class="close-btn">×</button>
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
        
        <!-- Sync Configuration -->
        <div class="config-section">
          <h3>📋 Sync Configuration</h3>
          <div class="config-grid">
            <div class="config-item">
              <label>Sync Frequency</label>
              <p>Every hour (automated)</p>
            </div>
            <div class="config-item">
              <label>Ticket Filter</label>
              <p>Subject starts with "NEW ONBOARDING"</p>
            </div>
            <div class="config-item">
              <label>Time Window</label>
              <p>Last 24 hours</p>
            </div>
            <div class="config-item">
              <label>Source System</label>
              <p>Freshservice API</p>
            </div>
          </div>
        </div>

        <!-- Freshservice Sync Logs -->
        <div class="config-section">
          <div class="logs-header">
            <h3>� Recent Sync Activity</h3>
            <span class="logs-subtitle">Last 5 runs ({{ syncLogs.length }} found)</span>
          </div>
          
          <div v-if="syncLogs.length === 0" class="empty-state">
            <div class="empty-icon">📝</div>
            <p>No sync history available</p>
            <small>Automated syncs run hourly</small>
          </div>
          
          <div v-else class="logs-table">
            <div class="table-header">
              <div class="col-status">Status</div>
              <div class="col-time">When</div>
              <div class="col-duration">Duration</div>
              <div class="col-trigger">Trigger</div>
              <div class="col-actions">Details</div>
            </div>
            
            <template v-for="(log, index) in syncLogs" :key="index">
              <div v-if="log"
                   class="table-row"
                   :class="{ 'has-details': log.output || log.error }"
              >
                <div class="col-status">
                  <div class="status-badge" :class="log.success ? 'success' : 'error'">
                    <span class="status-dot"></span>
                    {{ log.success ? 'Success' : 'Failed' }}
                  </div>
                </div>
              
              <div class="col-time">
                <div class="time-primary">{{ formatTime(log.executed_at) }}</div>
                <div class="time-secondary">{{ formatDate(log.executed_at) }}</div>
              </div>
              
              <div class="col-duration">
                <span v-if="log.execution_time" class="duration-text">
                  {{ log.execution_time }}s
                </span>
                <span v-else class="duration-text muted">—</span>
              </div>
              
              <div class="col-trigger">
                <div class="trigger-type">
                  {{ log.executed_by === 'Automated Scheduler' ? 'Auto' : 'Manual' }}
                </div>
              </div>
              
              <div class="col-actions">
                <button 
                  v-if="log.output || log.error"
                  @click="toggleSyncLogExpanded(index)"
                  class="details-btn"
                  :class="{ 'active': log.expanded }"
                >
                  <span class="btn-icon">{{ log.expanded ? '↑' : '↓' }}</span>
                  Details
                </button>
                <span v-else class="no-details">—</span>
              </div>
              </div>
            </template>
            
            <!-- Expandable details row -->
            <template v-for="(log, index) in syncLogs" :key="`details-${index}`">
              <div v-if="log && log.expanded && (log.output || log.error)"
                   class="details-row"
              >
              <div class="details-content">
                <div v-if="log.output" class="output-section">
                  <div class="output-header">
                    <span class="output-label">📋 Output</span>
                  </div>
                  <div class="output-content">{{ log.output }}</div>
                </div>
                
                <div v-if="log.error" class="error-section">
                  <div class="error-header">
                    <span class="error-label">⚠️ Error</span>
                  </div>
                  <div class="error-content">{{ log.error }}</div>
                </div>
              </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Placeholder for other settings tiles -->
    <div v-if="activeTile !== 'departments' && activeTile !== 'sync'" class="content-section">
      <div class="section-header">
        <h2>{{ getActiveTileTitle() }}</h2>
      </div>
      
      <div class="settings-content">
        <div class="coming-soon">
          <div class="coming-soon-icon">🚧</div>
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
      try {
        const response = await fetch('/api/v1/admin/scheduler/status')
        const data = await response.json()
        
        this.syncStatus = {
          running: data.scheduler_running || false,
          nextRun: data.next_freshservice_sync || null,
          totalJobs: data.total_scheduled_jobs || 0
        }
      } catch (error) {
        console.error('Error fetching sync status:', error)
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
        
        const data = await response.json()
        
        this.manualSyncResult = data
        
        if (data.success) {
          this.lastManualSync = {
            timestamp: new Date().toISOString(),
            result: data.result
          }
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
      try {
        const response = await fetch('/api/v1/admin/sync/freshservice/history')
        if (response.ok) {
          const data = await response.json()
          const logs = data.history || []
          
          // Transform backend logs to match frontend format and get last 5
          this.syncLogs = logs.slice(0, 5).map((log) => ({
            success: log.status === 'success',
            sync_type: 'Freshservice Onboarding Sync',
            executed_at: log.started_at || new Date().toISOString(),
            executed_by: log.executed_by === 'system_scheduler' ? 'Automated Scheduler' : (log.executed_by || 'Unknown'),
            execution_time: log.execution_time_seconds || null,
            output: log.output || '',
            error: log.error_message || '',
            expanded: false
          }))
          
          console.log('Sync logs loaded:', this.syncLogs.length)
        } else {
          console.error('Failed to fetch sync logs:', response.status)
          this.syncLogs = []
        }
      } catch (error) {
        console.error('Error fetching sync logs:', error)
        this.syncLogs = []
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

/* Settings Tiles */
.settings-tiles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.settings-tile {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.settings-tile:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.settings-tile.active {
  border-color: #667eea;
  background: #f8faff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.tile-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
  margin-top: 4px;
}

.tile-content {
  flex: 1;
}

.tile-content h3 {
  margin: 0 0 8px 0;
  color: #1f2937;
  font-size: 1.1rem;
  font-weight: 600;
}

.tile-content p {
  margin: 0 0 12px 0;
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.4;
}

.tile-count {
  display: inline-block;
  background: #667eea;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.settings-tile.active .tile-count {
  background: #5a67d8;
}

/* Coming Soon Placeholder */
.coming-soon {
  text-align: center;
  padding: 60px 40px;
  color: #6b7280;
}

.coming-soon-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.coming-soon h3 {
  margin: 0 0 12px 0;
  color: #374151;
  font-size: 1.5rem;
  font-weight: 600;
}

.coming-soon p {
  margin: 0;
  font-size: 1rem;
  line-height: 1.6;
  max-width: 400px;
  margin: 0 auto;
}

.content-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 24px;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.settings-content {
  padding: 30px;
}

/* Search and Filter */
.search-filter {
  display: flex;
  gap: 16px;
  margin-bottom: 30px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9rem;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Department List */
.department-list {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.list-header {
  display: grid;
  grid-template-columns: 1fr 2fr 120px;
  gap: 20px;
  padding: 16px 20px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

.department-row {
  display: grid;
  grid-template-columns: 1fr 2fr 120px;
  gap: 20px;
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
  align-items: center;
  transition: background-color 0.2s ease;
}

.department-row:hover {
  background: #f9fafb;
}

.department-row.editing {
  background: #eff6ff;
  border-color: #dbeafe;
}

.department-row:last-child {
  border-bottom: none;
}

.col-department {
  font-weight: 500;
  color: #1f2937;
}

.col-ou {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.ou-path {
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #374151;
}

.edit-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
}

.edit-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
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
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
}

.btn-edit:hover {
  background: #f3f4f6;
}

.btn-delete:hover {
  background: #fee2e2;
}

.btn-save:hover {
  background: #dcfce7;
}

.btn-cancel:hover {
  background: #fee2e2;
}

/* No Results */
.no-results {
  padding: 40px;
  text-align: center;
  color: #6b7280;
}

.no-results p {
  margin: 0;
  font-style: italic;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.info-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.info-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.info-content h3 {
  margin: 0 0 4px 0;
  color: #1f2937;
  font-size: 0.9rem;
  font-weight: 500;
}

.info-value {
  margin: 0;
  color: #667eea;
  font-size: 1.5rem;
  font-weight: 700;
}

/* Button Styles */
.btn-primary {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background: #5a67d8;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-outline {
  background: white;
  color: #667eea;
  border: 1px solid #667eea;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-outline:hover {
  background: #667eea;
  color: white;
}

/* Responsive Design */
@media (max-width: 768px) {
  .list-header,
  .department-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .col-actions {
    justify-content: flex-start;
  }
  
  .search-filter {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}

/* Sync Management Styles */
.sync-active {
  background: #10b981 !important;
  color: white !important;
}

.sync-status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.status-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.status-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.status-icon {
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #f3f4f6;
}

.status-icon.active {
  background: #d1fae5;
}

.status-content h3 {
  margin: 0 0 4px 0;
  color: #1f2937;
  font-size: 1.1rem;
  font-weight: 600;
}

.status-content p {
  margin: 0 0 4px 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.status-content small {
  color: #9ca3af;
  font-size: 0.8rem;
}

.sync-result-card {
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid #e5e7eb;
}

.sync-result-card.success {
  background: #ecfdf5;
  border-color: #10b981;
}

.sync-result-card.error {
  background: #fef2f2;
  border-color: #ef4444;
}

.result-header {
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 16px;
}

.result-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.1rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 4px;
}

.close-btn:hover {
  color: #374151;
}

.result-content p {
  margin: 0 0 16px 0;
  color: #374151;
}

.sync-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.processed-tickets h4 {
  margin: 0 0 12px 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
}

.ticket-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ticket-item {
  display: grid;
  grid-template-columns: 80px 1fr 1fr 120px;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.85rem;
}

.ticket-id {
  font-weight: 600;
  color: #667eea;
}

.ticket-user {
  color: #1f2937;
  font-weight: 500;
}

.ticket-email {
  color: #6b7280;
}

.ticket-dept {
  color: #9ca3af;
  text-align: right;
}

.config-section {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
}

.config-section h3 {
  margin: 0 0 20px 0;
  color: #1f2937;
  font-size: 1.2rem;
  font-weight: 600;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-item label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
}

.config-item p {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
}

/* Sync Logs Styles */
.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 16px;
}

.logs-header h3 {
  margin: 0;
  color: #374151;
  font-size: 1.1rem;
  font-weight: 600;
}

.logs-subtitle {
  color: #6b7280;
  font-size: 0.875rem;
}

.empty-state {
  text-align: center;
  padding: 32px 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px dashed #d1d5db;
}

.empty-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.empty-state p {
  margin: 0 0 4px 0;
  color: #374151;
  font-weight: 500;
}

.empty-state small {
  color: #6b7280;
}

.logs-table {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 100px 120px 80px 80px 80px;
  gap: 16px;
  padding: 12px 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table-row {
  display: grid;
  grid-template-columns: 100px 120px 80px 80px 80px;
  gap: 16px;
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  align-items: center;
  transition: background-color 0.15s ease;
}

.table-row:hover {
  background: #f9fafb;
}

.table-row:last-child {
  border-bottom: none;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 12px;
  width: fit-content;
}

.status-badge.success {
  background: #dcfce7;
  color: #166534;
}

.status-badge.error {
  background: #fee2e2;
  color: #dc2626;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-badge.success .status-dot {
  background: #16a34a;
}

.status-badge.error .status-dot {
  background: #dc2626;
}

.time-primary {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.time-secondary {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 2px;
}

.duration-text {
  font-size: 0.875rem;
  color: #374151;
  font-family: 'Monaco', 'Menlo', monospace;
}

.duration-text.muted {
  color: #9ca3af;
}

.trigger-type {
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: #f3f4f6;
  color: #374151;
  font-weight: 500;
  text-align: center;
}

.details-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 0.75rem;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.15s ease;
}

.details-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f8faff;
}

.details-btn.active {
  border-color: #667eea;
  color: #667eea;
  background: #eff6ff;
}

.btn-icon {
  font-size: 0.75rem;
}

.no-details {
  color: #9ca3af;
  font-size: 0.75rem;
  text-align: center;
}

.details-row {
  grid-column: 1 / -1;
  border-bottom: 1px solid #f3f4f6;
}

.details-content {
  padding: 16px;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
}

.output-section,
.error-section {
  margin-bottom: 12px;
}

.output-section:last-child,
.error-section:last-child {
  margin-bottom: 0;
}

.output-header,
.error-header {
  margin-bottom: 8px;
}

.output-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.error-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #dc2626;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.output-content,
.error-content {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 0.75rem;
  line-height: 1.4;
  color: #374151;
  white-space: pre-wrap;
  max-height: 150px;
  overflow-y: auto;
}
</style>
