<template>
  <div class="dashboard-layout">
    <!-- Sidebar Navigation -->
    <aside class="sidebar">
      <div class="logo">
        <img src="/hd-logo-200.png" alt="Helpdesk CRM" class="logo-image">
      </div>
      
      <nav class="navigation">
        <ul>
          <li>
            <router-link to="/dashboard" class="nav-item" :class="{ active: $route.path === '/dashboard' }">
              <i class="fas fa-tachometer-alt icon"></i>
              <span>Dashboard</span>
            </router-link>
          </li>
          <li>
            <router-link to="/onboarding" class="nav-item" :class="{ active: $route.path === '/onboarding' }">
              <i class="fas fa-user-plus icon"></i>
              <span>Onboard Users</span>
            </router-link>
          </li>
          <li>
            <router-link to="/print-onboarding" class="nav-item" :class="{ active: $route.path === '/print-onboarding' }">
              <i class="fas fa-print icon"></i>
              <span>Print Onboarding Info</span>
            </router-link>
          </li>

          <li>
            <router-link to="/offboarding" class="nav-item" :class="{ active: $route.path === '/offboarding' }">
              <i class="fas fa-user-minus icon"></i>
              <span>Offboard Users</span>
            </router-link>
          </li>
          <li>
            <router-link to="/offboarded-users" class="nav-item" :class="{ active: $route.path === '/offboarded-users' }">
              <i class="fas fa-users-slash icon"></i>
              <span>Offboarded Users Info</span>
            </router-link>
          </li>
                    <li>
            <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
              <i class="fas fa-cog icon"></i>
              <span>Settings</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content">
      <!-- Top Header -->
      <header class="top-header">
        <div class="header-left">
          <!-- <h1>{{ pageTitle }}</h1> -->
        </div>
        <div class="header-right">
          <!-- <div class="search-box">
            <input type="text" placeholder="Search tickets, customers..." v-model="searchQuery">
            <button class="search-btn">🔍</button>
          </div> -->
          <div class="user-menu" ref="userMenu">
            <div class="avatar">{{ userInitials }}</div>
            <span>{{ displayName }}</span>
            <div class="user-dropdown">
              <button class="dropdown-btn" @click="toggleDropdown">▼</button>
              <div v-if="showDropdown" class="dropdown-menu">
                <button @click="viewProfile" class="dropdown-item">
                  👤 Profile
                </button>
                <!-- <button @click="viewSettings" class="dropdown-item">
                  ⚙️ Settings
                </button> -->
                <div class="dropdown-divider"></div>
                <button @click="logout" class="dropdown-item logout-item">
                  🚪 Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Dashboard Content -->
      <div class="dashboard-content">
        <!-- Router View - Components will load here -->
        <router-view></router-view>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'DashboardLayout',
  data() {
    return {
      pageTitle: 'Dashboard',
      currentUser: 'Cristian Rodriguez', // Changed to your actual name
      searchQuery: '',
      showDropdown: false,
      iframeLoading: true,
      helpdeskUrl: 'https://helpdesk.americor.com/a/tickets/view/new_and_my_open', // Replace with your actual helpdesk URL
      stats: {
        totalTickets: 245,
        urgentTickets: 12,
        resolvedToday: 8,
        activeCustomers: 156
      },
      recentTickets: [
        {
          id: 1001,
          subject: 'Login issues with mobile app',
          customer: 'Alice Johnson',
          priority: 'High',
          status: 'Open',
          assignedTo: 'Mike Wilson',
          created: new Date('2025-07-30T10:30:00')
        },
        {
          id: 1002,
          subject: 'Payment processing error',
          customer: 'Bob Smith',
          priority: 'Critical',
          status: 'In Progress',
          assignedTo: 'Sarah Davis',
          created: new Date('2025-07-30T09:15:00')
        },
        {
          id: 1003,
          subject: 'Feature request: Dark mode',
          customer: 'Carol Brown',
          priority: 'Low',
          status: 'Open',
          assignedTo: 'Tom Anderson',
          created: new Date('2025-07-30T08:45:00')
        },
        {
          id: 1004,
          subject: 'Account verification problem',
          customer: 'David Wilson',
          priority: 'Medium',
          status: 'Resolved',
          assignedTo: 'Lisa Garcia',
          created: new Date('2025-07-29T16:20:00')
        }
      ]
    }
  },
  computed: {
    userInitials() {
      const name = Array.isArray(this.currentUser) ? this.currentUser[0] : this.currentUser
      return name
        .split(' ')
        .map(name => name.charAt(0))
        .join('')
        .toUpperCase()
    },
    displayName() {
      // Ensure we always display a clean string, not an array
      if (Array.isArray(this.currentUser)) {
        return this.currentUser[0] || 'User'
      }
      return this.currentUser || 'User'
    }
  },
  mounted() {
    // Get user data from session storage if available
    const userClaims = sessionStorage.getItem('userClaims')
    if (userClaims) {
      try {
        const claims = JSON.parse(userClaims)
        console.log('User claims received:', claims) // Debug log
        
        // Try different ways to get the user's name from JumpCloud claims
        let userName = ''
        
        if (claims.name) {
          userName = claims.name
        } else if (claims.given_name && claims.family_name) {
          userName = `${claims.given_name} ${claims.family_name}`
        } else if (claims.preferred_username) {
          userName = claims.preferred_username
        } else if (claims.email) {
          // Use email as fallback, but make it prettier
          userName = claims.email.split('@')[0].replace('.', ' ').replace('_', ' ')
        } else {
          userName = 'User'
        }
        
        this.currentUser = userName
        console.log('Set current user to:', userName) // Debug log
      } catch (error) {
        console.error('Error parsing user claims:', error)
      }
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  methods: {
    formatDate(date) {
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    },
    toggleDropdown() {
      this.showDropdown = !this.showDropdown
    },
    handleClickOutside(event) {
      // Check if click is outside the user menu
      const userMenu = this.$refs.userMenu
      if (userMenu && !userMenu.contains(event.target)) {
        this.showDropdown = false
      }
    },
    logout() {
      // Clear stored authentication data
      localStorage.removeItem('userToken')
      sessionStorage.removeItem('userClaims')
      
      // Redirect to login
      this.$router.push('/')
    },
    viewProfile() {
      this.showDropdown = false
      // TODO: Navigate to profile page
      console.log('Navigate to profile')
    },
    viewSettings() {
      this.showDropdown = false
      this.$router.push('/settings')
    },
    refreshIframe() {
      this.iframeLoading = true
      const iframe = this.$refs.helpdeskFrame
      if (iframe) {
        const currentSrc = iframe.src
        iframe.src = currentSrc
      }
    },
    openInNewTab() {
      window.open(this.helpdeskUrl, '_blank')
    },
    onIframeLoad() {
      this.iframeLoading = false
    },
    openHelpdesk() {
      window.open(this.helpdeskUrl, '_blank')
    },
    copyLink() {
      navigator.clipboard.writeText(this.helpdeskUrl).then(() => {
        // You could add a toast notification here
        alert('Link copied to clipboard!')
      }).catch(() => {
        alert('Failed to copy link')
      })
    },
    openNewTicket() {
      window.open('https://helpdesk.americor.com/a/tickets/new', '_blank')
    },
    openMyTickets() {
      window.open('https://helpdesk.americor.com/a/tickets/view/my_open', '_blank')
    },
    openUrgentTickets() {
      window.open('https://helpdesk.americor.com/a/tickets/view/urgent', '_blank')
    },
    openReports() {
      window.open('https://helpdesk.americor.com/a/reports', '_blank')
    }
  }
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  height: 100vh;
  background-color: #f5f7fa;
}

/* Sidebar Styles */
.sidebar {
  width: 250px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.logo {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
}

.logo-image {
  max-width: 150px;
  max-height: 60px;
  width: auto;
  height: auto;
  object-fit: contain;
}

.logo h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.navigation ul {
  list-style: none;
  padding: 0px 0;
  margin: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 400;
  transition: all 0.3s ease;
}

.nav-item:hover,
.nav-item.active {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item .icon {
  margin-right: 12px;
  font-size: 0.9rem;
}

/* Main Content Styles */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header Styles */
.top-header {
  background: white;
  padding: 10px 20px;
  border-bottom: 1px solid #c7c5c5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  background-color: #dddddd;
}

.header-left h1 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 6px 10px;
}

.search-box input {
  border: none;
  background: none;
  outline: none;
  padding: 4px 8px;
  width: 220px;
  font-size: 0.9rem;
}

.search-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  font-size: 0.9rem;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #e5e7eb;
  background: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.85rem;
}

.user-dropdown {
  position: relative;
}

.dropdown-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  min-width: 120px;
  margin-top: 4px;
}

.dropdown-item {
  width: 100%;
  padding: 12px 16px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  color: #374151;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
}

.dropdown-item:hover {
  background: #f9fafb;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 8px 0;
}

.logout-item {
  color: #dc2626;
}

.logout-item:hover {
  background: #fef2f2;
}

/* Dashboard Content Styles */
.dashboard-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
  border-left: 4px solid #667eea;
}

.stat-card.urgent {
  border-left-color: #ef4444;
}

.stat-icon {
  font-size: 2rem;
  opacity: 0.8;
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
  padding: 10px 16px;
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
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-right: 10px;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.header-actions {
  display: flex;
  align-items: center;
}

.iframe-container {
  position: relative;
  height: 800px;
  overflow: hidden;
}

.helpdesk-iframe {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 0 0 12px 12px;
}

.iframe-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.iframe-loading p {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0;
}

.helpdesk-access-content {
  padding: 30px;
}

.access-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.info-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  transition: all 0.3s ease;
}

.info-card:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-2px);
}

.info-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.info-content h3 {
  margin: 0 0 8px 0;
  color: #1f2937;
  font-size: 1.1rem;
  font-weight: 600;
}

.info-content p {
  margin: 0 0 16px 0;
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
}

.btn-outline {
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.btn-outline:hover {
  background: #667eea;
  color: white;
}

.status-info {
  background: #f0fdf4;
  color: #16a34a;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.quick-actions {
  border-top: 1px solid #e5e7eb;
  padding-top: 30px;
}

.quick-actions h3 {
  margin: 0 0 20px 0;
  color: #1f2937;
  font-size: 1.2rem;
  font-weight: 600;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-btn {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  color: #374151;
}

.action-btn:hover {
  border-color: #667eea;
  background: #f8fafc;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.action-icon {
  font-size: 1.3rem;
  flex-shrink: 0;
}

.tickets-table {
  overflow-x: auto;
}

.tickets-table table {
  width: 100%;
  border-collapse: collapse;
}

.tickets-table th,
.tickets-table td {
  text-align: left;
  padding: 12px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.tickets-table th {
  background: #f9fafb;
  color: #6b7280;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tickets-table tbody tr:hover {
  background: #f9fafb;
}

.priority-badge,
.status-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.priority-badge.critical {
  background: #fef2f2;
  color: #dc2626;
}

.priority-badge.high {
  background: #fef3c7;
  color: #d97706;
}

.priority-badge.medium {
  background: #dbeafe;
  color: #2563eb;
}

.priority-badge.low {
  background: #f0fdf4;
  color: #16a34a;
}

.status-badge.open {
  background: #eff6ff;
  color: #2563eb;
}

.status-badge.in-progress {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.resolved {
  background: #f0fdf4;
  color: #16a34a;
}

.status-badge.closed {
  background: #f3f4f6;
  color: #6b7280;
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-layout {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .header-right {
    flex-direction: column;
    gap: 10px;
  }
  
  .search-box input {
    width: 200px;
  }
}
</style>