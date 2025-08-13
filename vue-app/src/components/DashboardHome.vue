<template>
  <div class="dashboard-home">
    <!-- <div class="page-header">
      <div class="header-content">
        <h1><i class="fas fa-tachometer-alt"></i> Dashboard</h1>
        <p>Overview of onboarding activities and user statistics</p>
      </div>
    </div> -->

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>Loading dashboard data...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-banner">
      <div class="error-content">
        <i class="fas fa-exclamation-triangle error-icon"></i>
        <span>{{ error }}</span>
        <button @click="fetchDashboardData" class="retry-button">Retry</button>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Stats Cards -->
      <div class="stats-grid">
        <!-- Total Users Card -->
        <div class="stat-card">
          <div class="card-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="card-content">
            <h3>{{ stats.totalUsers }}</h3>
            <p>Total Users</p>
            <div class="card-meta">
              <span class="meta-badge">All time</span>
            </div>
          </div>
        </div>
        
        <!-- Completed Users Card -->
        <div class="stat-card">
          <div class="card-icon completed">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ stats.completedUsers }}</h3>
            <p>Completed</p>
            <div class="card-meta">
              <span class="meta-badge status-completed">
                <i class="fas fa-circle"></i>
                Active
              </span>
            </div>
          </div>
        </div>
        
        <!-- In Progress Card -->
        <div class="stat-card">
          <div class="card-icon in-progress">
            <i class="fas fa-spinner"></i>
          </div>
          <div class="card-content">
            <h3>{{ stats.inProgressUsers }}</h3>
            <p>In Progress</p>
            <div class="card-meta">
              <span class="meta-badge status-progress">
                <i class="fas fa-circle"></i>
                Processing
              </span>
            </div>
          </div>
        </div>
        
        <!-- Pending Card -->
        <div class="stat-card">
          <div class="card-icon pending">
            <i class="fas fa-hourglass-half"></i>
          </div>
          <div class="card-content">
            <h3>{{ stats.pendingUsers }}</h3>
            <p>Pending</p>
            <div class="card-meta">
              <span class="meta-badge status-pending">
                <i class="fas fa-circle"></i>
                Waiting
              </span>
            </div>
          </div>
        </div>
        
        <!-- Offboarded Card -->
        <div class="stat-card">
          <div class="card-icon offboarded">
            <i class="fas fa-user-times"></i>
          </div>
          <div class="card-content">
            <h3>{{ stats.offboardedUsers }}</h3>
            <p>Offboarded</p>
            <div class="card-meta">
              <span class="meta-badge status-offboarded">
                <i class="fas fa-circle"></i>
                Inactive
              </span>
            </div>
          </div>
        </div>
      </div>

    <!-- Quick Actions -->
    <div class="content-section">
      <div class="section-header">
        <div class="section-title">
          <i class="fas fa-bolt"></i>
          <h2>Quick Actions</h2>
        </div>
      </div>
      
      <div class="quick-actions-content">
        <div class="action-grid">
          <div class="action-card" @click="navigateTo('/onboarding')">
            <div class="action-icon">
              <i class="fas fa-user-plus"></i>
            </div>
            <div class="action-content">
              <h3>Onboard New User</h3>
              <p>Start the onboarding process for a new employee</p>
              <button class="btn-primary">Get Started <i class="fas fa-arrow-right"></i></button>
            </div>
          </div>
          
          <div class="action-card" @click="navigateTo('/print-onboarding')">
            <div class="action-icon">
              <i class="fas fa-print"></i>
            </div>
            <div class="action-content">
              <h3>Print Onboarding Info</h3>
              <p>Generate and print onboarding documentation</p>
              <button class="btn-primary">Print Info <i class="fas fa-arrow-right"></i></button>
            </div>
          </div>
          
          <div class="action-card" @click="navigateTo('/offboarding')">
            <div class="action-icon">
              <i class="fas fa-user-minus"></i>
            </div>
            <div class="action-content">
              <h3>Offboard User</h3>
              <p>Begin the offboarding process for departing employees</p>
              <button class="btn-primary">Start Process <i class="fas fa-arrow-right"></i></button>
            </div>
          </div>
          
          <div class="action-card" @click="navigateTo('/bulk-onboard')">
            <div class="action-icon">
              <i class="fas fa-users"></i>
            </div>
            <div class="action-content">
              <h3>Bulk Onboard Users</h3>
              <p>Upload and process multiple users for onboarding at once</p>
              <button class="btn-primary">Get Started <i class="fas fa-arrow-right"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Script Execution Logs -->
    <div class="content-section">
      <div class="section-header">
        <div class="section-title">
          <i class="fas fa-terminal"></i>
          <h2>Recent Script Executions</h2>
        </div>
        <div class="header-actions">
          <button class="btn-secondary" @click="fetchDashboardData">
            <i class="fas fa-sync-alt"></i>
            Refresh
          </button>
        </div>
      </div>
      
      <div class="activity-list-container">
        <div class="activity-list">
          <div v-if="recentActivities.length === 0" class="no-activity">
            <div class="no-activity-icon">
              <i class="fas fa-terminal"></i>
            </div>
            <p>No recent script executions to display</p>
          </div>
          <div v-else v-for="activity in recentActivities" :key="activity.id" class="activity-item">
            <div class="activity-icon" :class="[activity.type, getActivityStatusClass(activity)]">
              <i :class="getActivityIcon(activity)"></i>
            </div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-description">{{ getActivityDescription(activity) }}</div>
              <div class="activity-meta">
                <span class="activity-user">{{ activity.user }}</span>
                <span class="activity-time">{{ formatDate(activity.timestamp) }}</span>
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
export default {
  name: 'DashboardHome',
  data() {
    return {
      stats: {
        totalUsers: 0,
        completedUsers: 0,
        inProgressUsers: 0,
        pendingUsers: 0,
        offboardedUsers: 0
      },
      recentActivities: [],
      loading: true,
      error: null
    }
  },
  async mounted() {
    await this.fetchDashboardData()
  },
  methods: {
    async fetchDashboardData() {
      try {
        this.loading = true
        this.error = null
        
        // Fetch dashboard statistics
        const statsResponse = await fetch('/api/v1/dashboard/stats')
        if (!statsResponse.ok) {
          throw new Error('Failed to fetch dashboard statistics')
        }
        const statsData = await statsResponse.json()
        
        // Map the backend data to frontend properties
        this.stats = {
          totalUsers: statsData.totalUsers || 0,
          completedUsers: statsData.completedUsers || 0,
          inProgressUsers: statsData.inProgressUsers || 0,
          pendingUsers: statsData.pendingUsers || 0,
          offboardedUsers: statsData.offboardedUsers || 0
        }
        
        // Fetch real script execution logs instead of recent activity
        const logsResponse = await fetch('/api/v1/scripts/logs?limit=10')
        if (!logsResponse.ok) {
          throw new Error('Failed to fetch script execution logs')
        }
        const executionLogs = await logsResponse.json()
        
        // Transform execution logs into activity format
        this.recentActivities = executionLogs.map(log => ({
          id: log.id,
          type: 'script',
          title: `${log.script_type} - ${log.script_name}`,
          description: log.output || log.error_message || `Script executed`,
          status: log.status, // success, failed, running
          timestamp: log.completed_at || log.started_at,
          user: log.user_id ? `User ID: ${log.user_id}` : 'System',
          executedBy: log.executed_by
        })).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        this.error = error.message
        // Don't fall back to mock data - show the error instead
        this.recentActivities = []
      } finally {
        this.loading = false
      }
    },
    navigateTo(path) {
      this.$router.push(path)
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    },
    getActivityDescription(activity) {
      if (activity.type === 'script') {
        // Format script execution details
        const parts = []
        if (activity.description) parts.push(activity.description)
        if (activity.executedBy) parts.push(`Executed by ${activity.executedBy}`)
        return parts.join(' • ')
      } else if (activity.type === 'status_change') {
        return `${activity.description} • Updated by ${activity.updatedBy}`
      }
      return activity.description
    },
    getActivityStatusClass(activity) {
      if (activity.type === 'script') {
        switch(activity.status) {
          case 'success': return 'success'
          case 'failed': return 'error'  
          case 'running': return 'warning'
          default: return 'info'
        }
      }
      return 'info'
    },
    
    getActivityIcon(activity) {
      const iconMap = {
        script: 'fas fa-cogs',
        status_change: 'fas fa-exchange-alt',
        onboard: 'fas fa-user-plus',
        offboard: 'fas fa-user-minus',
        print: 'fas fa-print',
        default: 'fas fa-info-circle'
      }
      return iconMap[activity.type] || iconMap.default
    }
  }
}
</script>

<style scoped>
.dashboard-home {
  max-width: 1400px;
  margin: 0 auto;
  padding: 25px 16px;
  background: #f8fafc;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px 24px;
  color: white;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.header-content h1 {
  margin: 0 0 8px 0;
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
  font-size: 0.9rem;
  opacity: 0.9;
  font-weight: 300;
}

/* Loading and Error States */
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
  color: #6b7280;
}

.loading-spinner {
  width: 40px;
  height: 40px;
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

.error-banner {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.error-content {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #dc2626;
}

.error-icon {
  font-size: 1.2rem;
}

.retry-button {
  background: #dc2626;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  margin-left: auto;
  transition: background-color 0.3s ease;
}

.retry-button:hover {
  background: #b91c1c;
}

/* Stats Grid - Match SettingsView nav-card styling */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 80px;
}

.stat-card::before {
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

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.stat-card:hover::before {
  transform: scaleX(1);
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
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

.card-icon.completed {
  background: linear-gradient(135deg, #70f6a1 0%, #15803d 100%);
  box-shadow: 0 2px 8px rgba(22, 163, 74, 0.3);
}

.card-icon.in-progress {
  background: linear-gradient(135deg, #f4c174 0%, #f09630 100%);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.card-icon.pending {
  background: linear-gradient(135deg, #6be6f1 0%, #20b7c2 100%);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.card-icon.offboarded {
  background: linear-gradient(135deg, #f58181 0%, #fa3737 100%);
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
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
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1.2;
}

.card-content p {
  margin: 0 0 8px 0;
  color: #718096;
  font-size: 0.9rem;
  line-height: 1.3;
  font-weight: 500;
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

.meta-badge.status-completed {
  background: #16a34a;
}

.meta-badge.status-progress {
  background: #f59e0b;
}

.meta-badge.status-pending {
  background: #3b82f6;
}

.meta-badge.status-offboarded {
  background: #dc2626;
}

.meta-badge i {
  animation: pulse 2s infinite;
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

/* Buttons */
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

/* Quick Actions */
.quick-actions-content {
  padding: 20px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.action-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-height: 100px;
}

.action-card::before {
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

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.action-card:hover::before {
  transform: scaleX(1);
}

.action-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  color: white;
  font-size: 1.1rem;
}

.action-content {
  flex: 1;
  min-width: 0;
}

.action-content h3 {
  margin: 0 0 6px 0;
  color: #1a202c;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.2;
}

.action-content p {
  margin: 0 0 12px 0;
  color: #718096;
  font-size: 0.8rem;
  line-height: 1.3;
}

/* Activity List */
.activity-list-container {
  max-height: 400px;
  overflow-y: auto;
  border-radius: 8px;
}

.activity-list-container::-webkit-scrollbar {
  width: 6px;
}

.activity-list-container::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.activity-list-container::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
  transition: background 0.3s ease;
}

.activity-list-container::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

.activity-list {
  padding: 0;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s ease;
}

.activity-item:hover {
  background: #f8fafc;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.activity-icon.success {
  background: #dcfce7;
  color: #16a34a;
}

.activity-icon.error {
  background: #fee2e2;
  color: #dc2626;
}

.activity-icon.warning {
  background: #fef3c7;
  color: #d97706;
}

.activity-icon.info {
  background: #dbeafe;
  color: #2563eb;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 4px;
  font-size: 0.9rem;
}

.activity-description {
  color: #6b7280;
  font-size: 0.8rem;
  margin-bottom: 8px;
  line-height: 1.4;
}

.activity-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
}

.activity-user {
  color: #374151;
  font-weight: 500;
}

.activity-time {
  color: #9ca3af;
}

.no-activity {
  padding: 40px 20px;
  text-align: center;
  color: #6b7280;
}

.no-activity-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
  color: #94a3b8;
}

.no-activity p {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
  
  .action-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .dashboard-home {
    padding: 12px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
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
  
  .stat-card,
  .action-card {
    min-height: 70px;
    padding: 12px;
  }
  
  .card-icon,
  .action-icon {
    width: 36px;
    height: 36px;
  }
  
  .card-content h3 {
    font-size: 1.5rem;
  }
  
  .card-content p {
    font-size: 0.8rem;
  }
}
</style>
