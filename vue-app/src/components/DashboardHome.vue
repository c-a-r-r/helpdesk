<template>
  <div class="dashboard-home">
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
        <span class="error-icon">⚠️</span>
        <span>{{ error }}</span>
        <button @click="fetchDashboardData" class="retry-button">Retry</button>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-info">
          <h3>{{ stats.totalUsers }}</h3>
          <p>Total Users Onboarded</p>
        </div>
      </div>
      
      <div class="stat-card active">
        <div class="stat-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-info">
          <h3>{{ stats.activeUsers }}</h3>
          <p>Completed Users</p>
        </div>
      </div>
      
      <div class="stat-card pending">
        <div class="stat-icon">
          <i class="fas fa-hourglass-half"></i>
        </div>
        <div class="stat-info">
          <h3>{{ stats.pendingOnboarding }}</h3>
          <p>Pending Onboarding</p>
        </div>
      </div>
      
      <div class="stat-card offboarded">
        <div class="stat-icon">
          <i class="fas fa-user-times"></i>
        </div>
        <div class="stat-info">
          <h3>{{ stats.offboardedUsers }}</h3>
          <p>Offboarded Users</p>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="content-section">
      <div class="section-header">
        <h2>Quick Actions</h2>
      </div>
      
      <div class="quick-actions-content">
        <div class="action-grid">
          <div class="action-card" @click="navigateTo('/onboarding')">
            <div class="action-icon">👤➕</div>
            <div class="action-content">
              <h3>Onboard New User</h3>
              <p>Start the onboarding process for a new employee</p>
              <button class="btn-primary">Get Started →</button>
            </div>
          </div>
          
          <div class="action-card" @click="navigateTo('/print-onboarding')">
            <div class="action-icon">🖨️</div>
            <div class="action-content">
              <h3>Print Onboarding Info</h3>
              <p>Generate and print onboarding documentation</p>
              <button class="btn-primary">Print Info →</button>
            </div>
          </div>
          
          <div class="action-card" @click="navigateTo('/offboarding')">
            <div class="action-icon">👤➖</div>
            <div class="action-content">
              <h3>Offboard User</h3>
              <p>Begin the offboarding process for departing employees</p>
              <button class="btn-primary">Start Process →</button>
            </div>
          </div>
          
          <div class="action-card" @click="navigateTo('/offboarded-users')">
            <div class="action-icon">📋</div>
            <div class="action-content">
              <h3>View Offboarded Users</h3>
              <p>Review information about previously offboarded users</p>
              <button class="btn-primary">View List →</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="content-section">
      <div class="section-header">
        <h2>Recent Activity</h2>
        <button class="btn-secondary" @click="fetchDashboardData">Refresh</button>
      </div>
      
      <div class="activity-list">
        <div v-if="recentActivities.length === 0" class="no-activity">
          <div class="no-activity-icon">📝</div>
          <p>No recent activity to display</p>
        </div>
        <div v-else v-for="activity in recentActivities" :key="activity.id" class="activity-item">
          <div class="activity-icon" :class="[activity.type, getActivityStatusClass(activity)]">
            {{ activity.icon }}
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
</template>

<script>
export default {
  name: 'DashboardHome',
  data() {
    return {
      stats: {
        totalUsers: 0,
        activeUsers: 0,
        pendingOnboarding: 0,
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
          totalUsers: statsData.totalUsers,
          activeUsers: statsData.completedUsers, // Users who completed onboarding and are active (not offboarded)
          pendingOnboarding: statsData.pendingUsers + statsData.inProgressUsers, // Combine pending and in-progress
          offboardedUsers: statsData.offboardedUsers
        }
        
        // Fetch recent activity
        const activityResponse = await fetch('/api/v1/dashboard/recent-activity?limit=8')
        if (!activityResponse.ok) {
          throw new Error('Failed to fetch recent activity')
        }
        this.recentActivities = await activityResponse.json()
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        this.error = error.message
        // Fallback to mock data if API fails
        this.loadMockData()
      } finally {
        this.loading = false
      }
    },
    loadMockData() {
      // Fallback mock data for development
      this.stats = {
        totalUsers: 156,
        activeUsers: 142,
        pendingOnboarding: 8,
        offboardedUsers: 23
      }
      this.recentActivities = [
        {
          id: 'mock-1',
          type: 'script',
          icon: '⚙️',
          title: 'Script executed: create_user',
          description: 'JumpCloud script for John Smith',
          status: 'success',
          timestamp: new Date('2025-07-30T14:30:00').toISOString(),
          user: 'John Smith',
          executedBy: 'admin@company.com'
        },
        {
          id: 'mock-2',
          type: 'status_change',
          icon: '✅',
          title: 'Status updated: In Progress → Completed',
          description: 'Sarah Johnson onboarding completed',
          timestamp: new Date('2025-07-30T12:15:00').toISOString(),
          user: 'Sarah Johnson',
          updatedBy: 'hr@company.com'
        }
      ]
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
        return `${activity.description} • Executed by ${activity.executedBy}`
      } else if (activity.type === 'status_change') {
        return `${activity.description} • Updated by ${activity.updatedBy}`
      }
      return activity.description
    },
    getActivityStatusClass(activity) {
      if (activity.type === 'script') {
        return activity.status === 'success' ? 'success' : activity.status === 'failed' ? 'error' : 'warning'
      }
      return 'info'
    }
  }
}
</script>

<style scoped>
.dashboard-home {
  padding: 0;
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
}

.retry-button:hover {
  background: #b91c1c;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: rgb(236, 236, 236);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
  border-left: 4px solid #667eea;
}

.stat-card.active {
  border-left-color: #16a34a;
}

.stat-card.pending {
  border-left-color: #d97706;
}

.stat-card.offboarded {
  border-left-color: #dc2626;
}

.stat-icon {
  font-size: 2rem;
  opacity: 0.8;
  color: #667eea;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 50%;
}

.stat-card.active .stat-icon {
  color: #16a34a;
  background: rgba(22, 163, 74, 0.1);
}

.stat-card.pending .stat-icon {
  color: #d97706;
  background: rgba(217, 119, 6, 0.1);
}

.stat-card.offboarded .stat-icon {
  color: #dc2626;
  background: rgba(220, 38, 38, 0.1);
}

.stat-info h3 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
}

.stat-info p {
  margin: 5px 0 0 0;
  color: #6b7280;
  font-size: 0.9rem;
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

.btn-primary {
  background: #667eea;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background: #5a67d8;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.quick-actions-content {
  padding: 30px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.action-card {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.action-card:hover {
  background: #f1f5f9;
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.action-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.action-content h3 {
  margin: 0 0 8px 0;
  color: #1f2937;
  font-size: 1.1rem;
  font-weight: 600;
}

.action-content p {
  margin: 0 0 16px 0;
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
}

.activity-list {
  padding: 0;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.2s ease;
}

.activity-item:hover {
  background: #f9fafb;
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
  font-size: 1.2rem;
  flex-shrink: 0;
}

.activity-icon.onboard {
  background: #f0fdf4;
}

.activity-icon.offboard {
  background: #fef2f2;
}

.activity-icon.print {
  background: #eff6ff;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.activity-description {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.activity-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
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
  font-size: 2rem;
  margin-bottom: 12px;
}
</style>
