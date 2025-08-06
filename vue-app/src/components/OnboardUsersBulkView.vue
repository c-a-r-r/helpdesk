<template>
  <div class="bulk-onboarding-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>Bulk Onboarding Management</h1>
          <p>Manage multiple user onboarding processes simultaneously</p>
        </div>
        <router-link v-if="canCreate" to="/onboarding/create" class="btn-primary">
          <i class="fa-solid fa-plus"></i> Add New User
        </router-link>
      </div>
    </div>

    <!-- Bulk Action Controls -->
    <div class="bulk-actions-section">
      <div class="bulk-header">
        <div class="selection-info">
          <span class="selected-count">{{ selectedUsers.length }} user(s) selected</span>
          <button 
            v-if="selectedUsers.length > 0" 
            @click="clearSelection" 
            class="btn-clear"
          >
            Clear Selection
          </button>
        </div>
        <div class="bulk-buttons">
          <button 
            @click="bulkCreateJumpcloud" 
            :disabled="selectedUsers.length === 0"
            class="btn-bulk btn-jumpcloud"
            :class="{ disabled: selectedUsers.length === 0 }"
          >
            <i class="fa-solid fa-cloud"></i> Create JumpCloud Accounts ({{ selectedUsers.length }})
          </button>
          <button 
            @click="bulkCreateGoogle" 
            :disabled="selectedUsers.length === 0"
            class="btn-bulk btn-google"
            :class="{ disabled: selectedUsers.length === 0 }"
          >
            <i class="fa-brands fa-google"></i> Create Google Accounts ({{ selectedUsers.length }})
          </button>
        </div>
      </div>
    </div>

    <!-- Onboarding Records Table -->
    <div class="content-section">
      <div class="section-header">
        <h2>Onboarding Records</h2>
        <div class="header-actions">
          <div class="records-per-page">
            <label for="recordsPerPage">Show:</label>
            <select id="recordsPerPage" v-model="recordsPerPage" class="records-select">
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
            <span>records</span>
          </div>
          <div class="status-filter">
            <label for="statusFilter">Status:</label>
            <select id="statusFilter" v-model="statusFilter" class="status-select">
              <option value="">All</option>
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="Search users..."
            class="search-input"
          >
          <button class="btn-secondary" @click="fetchOnboardingData">
            <i class="fa-solid fa-arrows-rotate"></i> Refresh
          </button>
        </div>
      </div>
      
      <div v-if="loading" class="loading-state">
        <p>Loading onboarding data...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <p>Error loading data: {{ error }}</p>
        <button class="btn-outline" @click="fetchOnboardingData">Try Again</button>
      </div>
      
      <div v-else-if="onboardingData.length === 0" class="empty-state">
        <p>No onboarding records found.</p>
      </div>
      
      <div v-else-if="filteredOnboardingData.length === 0" class="empty-state">
        <p>No records match your current filters.</p>
        <button class="btn-outline" @click="clearFilters">Clear Filters</button>
      </div>
      
      <div v-else class="table-container">
        <!-- Pagination Info -->
        <div class="pagination-info">
          <span>
            Displaying {{ (currentPage - 1) * parseInt(recordsPerPage) + 1 }} - 
            {{ Math.min(currentPage * parseInt(recordsPerPage), totalRecords) }} of {{ totalRecords }} records
          </span>
          <div class="pagination-controls">
            <span>Page {{ currentPage }} / {{ totalPages }}</span>
            <button 
              class="btn-page" 
              @click="previousPage" 
              :disabled="currentPage === 1"
            >
              <i class="fa-solid fa-chevron-left"></i> Previous
            </button>
            <button 
              class="btn-page" 
              @click="nextPage" 
              :disabled="currentPage === totalPages"
            >
              Next <i class="fa-solid fa-chevron-right"></i>
            </button>
          </div>
        </div>
        
        <table class="data-table">
          <thead>
            <tr>
              <th class="checkbox-column">
                <input 
                  type="checkbox" 
                  @change="toggleSelectAll"
                  :checked="isAllSelected"
                  :indeterminate="isPartiallySelected"
                  class="bulk-checkbox"
                >
              </th>
              <!-- <th>Ticket #</th> -->
              <th>Name</th>
              <th>Company Email</th>
              <th>Department</th>
              <th>Title</th>
              <th>Username</th>
              <!-- <th class="sortable" @click="sortByStatus">
                Status 
                <i class="fa-solid fa-sort" v-if="!statusSortOrder"></i>
                <i class="fa-solid fa-sort-up" v-if="statusSortOrder === 'asc'"></i>
                <i class="fa-solid fa-sort-down" v-if="statusSortOrder === 'desc'"></i>
              </th> -->
              <th>JumpCloud</th>
              <th>Google Workspace</th>
              <th>Created By</th>
              <th>Start Date</th>
              <th v-if="canEdit || canDelete" class="action-column">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedData" :key="user.id" :class="{ selected: isUserSelected(user.id) }">
              <td class="checkbox-column">
                <input 
                  type="checkbox" 
                  :checked="isUserSelected(user.id)"
                  @change="toggleUserSelection(user)"
                  class="user-checkbox"
                >
              </td>
              <!-- <td>{{ user.ticket_number || 'N/A' }}</td> -->
              <td>{{ user.first_name }} {{ user.last_name }}</td>
              <td>{{ user.company_email || 'N/A' }}</td>
              <td>{{ user.department }}</td>
              <td>{{ user.title }}</td>
              <td>{{ user.username }}</td>
              <!-- <td>
                <span :class="getStatusClass(user.status)">
                  {{ user.status || 'Pending' }}
                </span>
              </td> -->
              <td>
                <div class="account-status">
                  <span v-if="user.jumpcloud_status" :class="getAccountStatusClass(user.jumpcloud_status)">
                    <i :class="getAccountStatusIcon(user.jumpcloud_status)"></i>
                    {{ getAccountStatusText(user.jumpcloud_status) }}
                  </span>
                  <span v-else class="status-not-created">
                    <i class="fa-solid fa-minus"></i> Not Created
                  </span>
                  <div v-if="user.jumpcloud_error" class="error-details" :title="user.jumpcloud_error">
                    <i class="fa-solid fa-exclamation-triangle"></i> Error
                  </div>
                </div>
              </td>
              <td>
                <div class="account-status">
                  <span v-if="user.google_status" :class="getAccountStatusClass(user.google_status)">
                    <i :class="getAccountStatusIcon(user.google_status)"></i>
                    {{ getAccountStatusText(user.google_status) }}
                  </span>
                  <span v-else class="status-not-created">
                    <i class="fa-solid fa-minus"></i> Not Created
                  </span>
                  <div v-if="user.google_error" class="error-details" :title="user.google_error">
                    <i class="fa-solid fa-exclamation-triangle"></i> Error
                  </div>
                </div>
              </td>
              <td>
                <span v-if="user.created_by === 'freshdesk-sync'" class="sync-indicator">
                  <i class="fa-solid fa-sync"></i> Freshdesk Sync
                </span>
                <span v-else-if="user.created_by" class="user-indicator">
                  <i class="fa-solid fa-user"></i> {{ user.created_by }}
                </span>
                <span v-else class="unknown-indicator">
                  <i class="fa-solid fa-question"></i> Unknown
                </span>
              </td>
              <td>{{ formatDate(user.start_date) }}</td>
              <td v-if="canEdit || canDelete" class="action-buttons">
                <!-- <button v-if="canEdit" class="btn-action btn-edit" @click="editUser(user)" title="Edit User">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button> -->
                <button v-if="canDelete" class="btn-action btn-delete" @click="deleteUser(user)" title="Delete User">
                  <i class="fa-solid fa-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Bulk Progress Modal -->
    <div v-if="showBulkProgress" class="modal-overlay">
      <div class="modal-content progress-modal">
        <div class="modal-header">
          <h3>{{ bulkOperation }} Progress</h3>
        </div>
        <div class="modal-body">
          <div class="progress-container">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: (bulkProgress / selectedUsers.length * 100) + '%' }"
              ></div>
            </div>
            <div class="progress-text">
              {{ bulkProgress }} / {{ selectedUsers.length }} users processed
            </div>
          </div>
          
          <div class="progress-details">
            <div v-for="result in bulkResults" :key="result.user.id" class="progress-item">
              <span class="user-name">{{ result.user.first_name }} {{ result.user.last_name }}</span>
              <span :class="['status', result.success ? 'success' : 'error']">
                <i :class="result.success ? 'fa-solid fa-check' : 'fa-solid fa-times'"></i>
                {{ result.message }}
              </span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button 
            v-if="bulkProgress === selectedUsers.length" 
            @click="closeBulkProgress" 
            class="btn-primary"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'OnboardUsersBulkView',
  data() {
    return {
      onboardingData: [],
      selectedUsers: [],
      loading: false,
      error: null,
      searchQuery: '',
      statusFilter: '',
      recordsPerPage: 25,
      currentPage: 1,
      statusSortOrder: null,
      showBulkProgress: false,
      bulkOperation: '',
      bulkProgress: 0,
      bulkResults: []
    }
  },
  computed: {
    filteredOnboardingData() {
      let filtered = this.onboardingData.filter(user => 
        user && user.id && (user.first_name || user.last_name || user.company_email)
      )
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(user => 
          user.first_name?.toLowerCase().includes(query) ||
          user.last_name?.toLowerCase().includes(query) ||
          user.personal_email?.toLowerCase().includes(query) ||
          user.company_email?.toLowerCase().includes(query) ||
          user.department?.toLowerCase().includes(query) ||
          user.title?.toLowerCase().includes(query) ||
          user.username?.toLowerCase().includes(query) ||
          user.manager?.toLowerCase().includes(query)
        )
      }
      
      if (this.statusFilter) {
        filtered = filtered.filter(user => 
          (user.status || 'Pending') === this.statusFilter
        )
      }
      
      if (this.statusSortOrder) {
        filtered = [...filtered].sort((a, b) => {
          const statusA = a.status || 'Pending'
          const statusB = b.status || 'Pending'
          const statusOrder = ['Pending', 'In Progress', 'Completed', 'Cancelled']
          
          const indexA = statusOrder.indexOf(statusA)
          const indexB = statusOrder.indexOf(statusB)
          
          if (this.statusSortOrder === 'asc') {
            return indexA - indexB
          } else {
            return indexB - indexA
          }
        })
      }
      
      return filtered
    },
    
    totalRecords() {
      return this.filteredOnboardingData.length
    },
    
    totalPages() {
      return Math.ceil(this.totalRecords / parseInt(this.recordsPerPage))
    },
    
    paginatedData() {
      const start = (this.currentPage - 1) * parseInt(this.recordsPerPage)
      const end = start + parseInt(this.recordsPerPage)
      return this.filteredOnboardingData.slice(start, end)
    },

    isAllSelected() {
      return this.paginatedData.length > 0 && this.paginatedData.every(user => this.isUserSelected(user.id))
    },

    isPartiallySelected() {
      return this.paginatedData.some(user => this.isUserSelected(user.id)) && !this.isAllSelected
    },
    
    currentUser() {
      return this.getCurrentUser()
    },
    
    canEdit() {
      const user = this.currentUser
      return user ? this.hasEditPermission() : false
    },
    
    canDelete() {
      const user = this.currentUser
      return user ? this.hasDeletePermission() : false
    },
    
    canCreate() {
      const user = this.currentUser
      return user ? this.hasCreatePermission() : false
    }
  },
  mounted() {
    this.fetchOnboardingData()
  },
  watch: {
    searchQuery() {
      this.currentPage = 1
    },
    
    statusFilter() {
      this.currentPage = 1
    },
    
    recordsPerPage() {
      this.recordsPerPage = parseInt(this.recordsPerPage)
      this.currentPage = 1
    }
  },
  methods: {
    async fetchOnboardingData() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/v1/onboarding/')
        let rawData = response.data
        if (!Array.isArray(rawData)) {
          if (rawData && rawData.data && Array.isArray(rawData.data)) {
            rawData = rawData.data
          } else {
            rawData = rawData ? [rawData] : []
          }
        }
        
        const validData = rawData.filter(user => 
          user && user.id && (user.first_name || user.last_name || user.company_email)
        )
        
        const sortedData = validData.sort((a, b) => b.id - a.id)
        this.onboardingData = sortedData
      } catch (error) {
        console.error('Error fetching onboarding data:', error)
        this.error = error.response?.data?.detail || error.message || 'Failed to fetch data'
      } finally {
        this.loading = false
      }
    },

    isUserSelected(userId) {
      return this.selectedUsers.some(user => user.id === userId)
    },

    toggleUserSelection(user) {
      const index = this.selectedUsers.findIndex(selected => selected.id === user.id)
      if (index > -1) {
        this.selectedUsers.splice(index, 1)
      } else {
        this.selectedUsers.push(user)
      }
    },

    toggleSelectAll() {
      if (this.isAllSelected) {
        // Deselect all on current page
        this.paginatedData.forEach(user => {
          const index = this.selectedUsers.findIndex(selected => selected.id === user.id)
          if (index > -1) {
            this.selectedUsers.splice(index, 1)
          }
        })
      } else {
        // Select all on current page
        this.paginatedData.forEach(user => {
          if (!this.isUserSelected(user.id)) {
            this.selectedUsers.push(user)
          }
        })
      }
    },

    clearSelection() {
      this.selectedUsers = []
    },

    async bulkCreateJumpcloud() {
      if (this.selectedUsers.length === 0) return
      
      this.bulkOperation = 'JumpCloud Account Creation'
      this.showBulkProgress = true
      this.bulkProgress = 0
      this.bulkResults = []

      for (const user of this.selectedUsers) {
        try {
          const currentUserEmail = this.getCurrentUserEmail()
          const response = await axios.post('/api/v1/scripts/jumpcloud/create-user', {
            script_type: "jumpcloud",
            script_name: "create_user",
            user_id: user.id,
            additional_params: {}
          }, {
            params: {
              user_email: currentUserEmail
            }
          })
          
          this.bulkResults.push({
            user: user,
            success: true,
            message: 'Account created successfully'
          })
        } catch (error) {
          this.bulkResults.push({
            user: user,
            success: false,
            message: error.response?.data?.detail || 'Failed to create account'
          })
        }
        
        this.bulkProgress++
        
        // Refresh data to show updated account status
        await this.fetchOnboardingData()
      }
    },

    async bulkCreateGoogle() {
      if (this.selectedUsers.length === 0) return
      
      this.bulkOperation = 'Google Workspace Account Creation'
      this.showBulkProgress = true
      this.bulkProgress = 0
      this.bulkResults = []

      for (const user of this.selectedUsers) {
        try {
          const currentUserEmail = this.getCurrentUserEmail()
          const response = await axios.post('/api/v1/scripts/google/create-user', {
            script_type: "google",
            script_name: "create_user",
            user_id: user.id,
            additional_params: {}
          }, {
            params: {
              user_email: currentUserEmail
            }
          })
          
          this.bulkResults.push({
            user: user,
            success: true,
            message: 'Account created successfully'
          })
        } catch (error) {
          this.bulkResults.push({
            user: user,
            success: false,
            message: error.response?.data?.detail || 'Failed to create account'
          })
        }
        
        this.bulkProgress++
        
        // Refresh data to show updated account status
        await this.fetchOnboardingData()
      }
    },

    closeBulkProgress() {
      this.showBulkProgress = false
      this.clearSelection()
      this.fetchOnboardingData() // Refresh data after bulk operations
    },

    editUser(user) {
      this.$router.push({
        name: 'edit-user',
        params: { userId: user.id }
      })
    },

    async deleteUser(user) {
      if (confirm(`Are you sure you want to delete ${user.first_name} ${user.last_name}?`)) {
        try {
          const currentUserEmail = this.getCurrentUserEmail()
          await axios.delete(`/api/v1/onboarding/${user.id}?user_email=${encodeURIComponent(currentUserEmail)}`)
          alert('User deleted successfully!')
          await this.fetchOnboardingData()
        } catch (error) {
          console.error('Error deleting user:', error)
          alert('Error deleting user: ' + (error.response?.data?.detail || error.message))
        }
      }
    },

    getStatusClass(status) {
      const statusClass = {
        'Pending': 'status-pending',
        'In Progress': 'status-progress',
        'Completed': 'status-completed',
        'Cancelled': 'status-cancelled'
      }
      return statusClass[status] || 'status-pending'
    },

    sortByStatus() {
      if (this.statusSortOrder === null) {
        this.statusSortOrder = 'asc'
      } else if (this.statusSortOrder === 'asc') {
        this.statusSortOrder = 'desc'
      } else {
        this.statusSortOrder = null
      }
      this.currentPage = 1
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
    },

    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },

    clearFilters() {
      this.searchQuery = ''
      this.statusFilter = ''
      this.statusSortOrder = null
      this.currentPage = 1
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        return new Date(dateString).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        })
      } catch {
        return 'Invalid Date'
      }
    },

    // Authentication methods (similar to OnboardingView)
    getCurrentUserEmail() {
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
          if (claims.given_name && claims.family_name) {
            const firstName = Array.isArray(claims.given_name) ? claims.given_name[0] : claims.given_name
            const lastName = Array.isArray(claims.family_name) ? claims.family_name[0] : claims.family_name
            const constructedEmail = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@americor.com`
            return constructedEmail
          }
        } catch (error) {
          console.error('Error parsing JumpCloud SSO claims:', error)
        }
      }
      
      if (process.env.NODE_ENV === 'development') {
        return 'cristian.rodriguez@americor.com'
      }
      
      throw new Error('User not authenticated via SSO')
    },

    getCurrentUser() {
      const userClaims = sessionStorage.getItem('userClaims')
      if (userClaims) {
        try {
          const claims = JSON.parse(userClaims)
          return {
            email: this.getCurrentUserEmail(),
            name: claims.name || `${claims.given_name || ''} ${claims.family_name || ''}`.trim(),
            groups: claims.groups || [],
            role: this.determineUserRole(claims)
          }
        } catch (error) {
          console.error('Error parsing user claims:', error)
        }
      }
      
      if (process.env.NODE_ENV === 'development') {
        return {
          email: 'cristian.rodriguez@americor.com',
          name: 'Cristian Rodriguez',
          groups: ['Help Desk Management Tool - Admin'],
          role: 'ADMIN'
        }
      }
      
      return null
    },

    determineUserRole(claims) {
      const groups = claims.groups || []
      const roleAttribute = claims.Role || claims.role
      
      let allRoles = Array.isArray(groups) ? [...groups] : [groups]
      if (roleAttribute) {
        if (Array.isArray(roleAttribute)) {
          allRoles = allRoles.concat(roleAttribute)
        } else {
          allRoles.push(roleAttribute)
        }
      }
      
      for (const roleOrGroup of allRoles) {
        const roleLower = roleOrGroup?.toString().toLowerCase() || ''
        
        if (roleLower === "help desk management tool - admin" || roleLower === "admin") {
          return 'ADMIN'
        } else if (roleLower === "help desk management tool - it" || roleLower === "it") {
          return 'IT'
        } else if (roleLower.includes('admin')) {
          return 'ADMIN'
        } else if (roleLower.includes('it') || roleLower.includes('information technology')) {
          return 'IT'
        }
      }
      
      return 'USER'
    },

    hasCreatePermission() {
      const user = this.currentUser
      if (!user) return false
      const role = user.role
      return role === 'ADMIN' || role === 'IT'
    },

    hasEditPermission() {
      const user = this.currentUser
      if (!user) return false
      const role = user.role
      return role === 'ADMIN' || role === 'IT'
    },

    hasDeletePermission() {
      const user = this.currentUser
      if (!user) return false
      const role = user.role
      return role === 'ADMIN'
    },

    // Account status helper methods
    getAccountStatusClass(status) {
      const statusClass = {
        'SUCCESS': 'account-status-success',
        'FAILED': 'account-status-failed',
        'RUNNING': 'account-status-running',
        'PENDING': 'account-status-pending',
        // Keep lowercase for backward compatibility
        'success': 'account-status-success',
        'failed': 'account-status-failed',
        'running': 'account-status-running',
        'pending': 'account-status-pending'
      }
      return statusClass[status] || 'account-status-unknown'
    },

    getAccountStatusIcon(status) {
      const statusIcon = {
        'SUCCESS': 'fa-solid fa-check-circle',
        'FAILED': 'fa-solid fa-times-circle',
        'RUNNING': 'fa-solid fa-spinner fa-spin',
        'PENDING': 'fa-solid fa-clock',
        // Keep lowercase for backward compatibility
        'success': 'fa-solid fa-check-circle',
        'failed': 'fa-solid fa-times-circle',
        'running': 'fa-solid fa-spinner fa-spin',
        'pending': 'fa-solid fa-clock'
      }
      return statusIcon[status] || 'fa-solid fa-question-circle'
    },

    getAccountStatusText(status) {
      const statusText = {
        'SUCCESS': 'Created',
        'FAILED': 'Failed',
        'RUNNING': 'Creating...',
        'PENDING': 'Pending',
        // Keep lowercase for backward compatibility
        'success': 'Created',
        'failed': 'Failed',
        'running': 'Creating...',
        'pending': 'Pending'
      }
      return statusText[status] || 'Unknown'
    }
  }
}
</script>

<style scoped>
/* Import all base styles from OnboardingView and add bulk-specific styles */
.bulk-onboarding-page {
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

/* Bulk Actions Section */
.bulk-actions-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.bulk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selected-count {
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
}

.btn-clear {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-clear:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.bulk-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-bulk {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-jumpcloud {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
}

.btn-jumpcloud:hover:not(.disabled) {
  background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(249, 115, 22, 0.4);
}

.btn-google {
  background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
  color: white;
}

.btn-google:hover:not(.disabled) {
  background: linear-gradient(135deg, #1a73e8 0%, #137333 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(66, 133, 244, 0.4);
}

.btn-bulk.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

/* Checkbox Column Styles */
.checkbox-column {
  width: 50px;
  text-align: center;
}

.bulk-checkbox,
.user-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #667eea;
}

.bulk-checkbox:indeterminate {
  accent-color: #f59e0b;
}

/* Selected Row Styling */
tr.selected {
  background-color: #f0f9ff !important;
  border-left: 4px solid #667eea;
}

tr.selected:hover {
  background-color: #e0f2fe !important;
}

/* Progress Modal Styles */
.progress-modal {
  max-width: 600px;
  width: 90vw;
}

.progress-container {
  margin-bottom: 24px;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 500;
}

.progress-details {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
}

.progress-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.progress-item:last-child {
  border-bottom: none;
}

.user-name {
  font-weight: 500;
  color: #1f2937;
}

.status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status.success {
  color: #059669;
}

.status.error {
  color: #dc2626;
}

/* Base table and component styles - inheriting from OnboardingView */
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

.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.records-per-page,
.status-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #374151;
}

.records-select,
.status-select {
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.9rem;
  background: white;
  min-width: 70px;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  min-width: 200px;
}

.loading-state,
.error-state,
.empty-state {
  padding: 40px;
  text-align: center;
  color: #6b7280;
}

.table-container {
  overflow-x: auto;
}

.pagination-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.9rem;
  color: #374151;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-page {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-page:hover:not(:disabled) {
  background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75rem;
}

.data-table th {
  background: #f9fafb;
  padding: 8px 10px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  border-right: 1px solid #e5e7eb;
  font-size: 0.75rem;
}

.data-table th:last-child {
  border-right: none;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
}

.data-table th.sortable:hover {
  background: #f3f4f6;
}

.data-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #f3f4f6;
  border-right: 1px solid #f3f4f6;
  color: #1f2937;
  font-size: 0.75rem;
}

.data-table td:last-child {
  border-right: none;
}

.data-table tbody tr:hover {
  background: #f9fafb;
}

/* Button Styles */
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
  text-decoration: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

.btn-secondary {
  background: #f8fafc;
  color: #475569;
  border: 2px solid #e2e8f0;
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn-outline {
  background: white;
  color: #667eea;
  border: 1px solid #667eea;
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

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.btn-action {
  padding: 4px 6px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.7rem;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
}

.btn-edit {
  background: #3b82f6;
  color: white;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.btn-edit:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
}

.btn-delete {
  background: #ef4444;
  color: white;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}

.btn-delete:hover {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.4);
}

/* Status badges */
.status-pending {
  background: #fef3c7;
  color: #92400e;
  padding: 1px 6px;
  border-radius: 8px;
  font-size: 0.65rem;
  font-weight: 500;
}

.status-progress {
  background: #dbeafe;
  color: #1e40af;
  padding: 1px 6px;
  border-radius: 8px;
  font-size: 0.65rem;
  font-weight: 500;
}

.status-completed {
  background: #dcfce7;
  color: #166534;
  padding: 1px 6px;
  border-radius: 8px;
  font-size: 0.65rem;
  font-weight: 500;
}

.status-cancelled {
  background: #fee2e2;
  color: #dc2626;
  padding: 1px 6px;
  border-radius: 8px;
  font-size: 0.65rem;
  font-weight: 500;
}

/* Created by indicators */
.sync-indicator {
  background: #e0f2fe;
  color: #0277bd;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.user-indicator {
  background: #f3e8ff;
  color: #7c3aed;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.unknown-indicator {
  background: #f3f4f6;
  color: #6b7280;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.action-column {
  width: 90px;
  text-align: center;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.3rem;
  font-weight: 600;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .bulk-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .bulk-buttons {
    justify-content: stretch;
  }
  
  .btn-bulk {
    flex: 1;
    justify-content: center;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .pagination-info {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .data-table {
    font-size: 0.7rem;
  }
  
  .data-table th,
  .data-table td {
    padding: 6px 4px;
  }
  
  .checkbox-column {
    width: 40px;
  }
  
  .bulk-checkbox,
  .user-checkbox {
    width: 16px;
    height: 16px;
  }
}

/* Account Status Styles */
.account-status {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
}

.account-status-success {
  background: #dcfce7;
  color: #166534;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.account-status-failed {
  background: #fef2f2;
  color: #dc2626;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.account-status-running {
  background: #fef3c7;
  color: #d97706;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.account-status-pending {
  background: #f0f9ff;
  color: #0284c7;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.status-not-created {
  background: #f3f4f6;
  color: #6b7280;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.error-details {
  background: #fef2f2;
  color: #dc2626;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 0.65rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  cursor: help;
}
</style>
