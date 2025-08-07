<template>
  <div class="offboarding-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>Offboarding Management</h1>
          <p>Manage user offboarding process and records</p>
        </div>
        <router-link v-if="canCreate" to="/offboarding/create" class="btn-primary">
          <i class="fa-solid fa-plus"></i> Add New Offboarding
        </router-link>
      </div>
    </div>

    <!-- Offboarding Records Table -->
    <div class="content-section">
      <div class="section-header">
        <h2>Offboarding Records</h2>
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
              <option value="Failed">Failed</option>
            </select>
          </div>
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="Search users..."
            class="search-input"
          >
          <button class="btn-secondary" @click="fetchOffboardingData">
            <i class="fa-solid fa-arrows-rotate"></i> Refresh
          </button>
        </div>
      </div>
      
      <div v-if="loading" class="loading-state">
        <p>Loading offboarding data...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <p>Error loading data: {{ error }}</p>
        <button class="btn-outline" @click="fetchOffboardingData">Try Again</button>
      </div>
      
      <div v-else-if="offboardingData.length === 0" class="empty-state">
        <p>No offboarding records found.</p>
      </div>
      
      <div v-else-if="filteredOffboardingData.length === 0" class="empty-state">
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
              <th>Name</th>
              <th>Company Email</th>
              <th>Hostname</th>
              <th>Requested By</th>
              <th>Password</th>
              <th>Created By</th>
              <th class="sortable" @click="sortByStatus">
                Status 
                <i class="fa-solid fa-sort" v-if="!statusSortOrder"></i>
                <i class="fa-solid fa-sort-up" v-if="statusSortOrder === 'asc'"></i>
                <i class="fa-solid fa-sort-down" v-if="statusSortOrder === 'desc'"></i>
              </th>
              <th>Date Created</th>
              <th v-if="canEdit || canDelete" class="action-column">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedData" :key="user.id">
              <td>{{ user.first_name }} {{ user.last_name }}</td>
              <td>{{ user.company_email }}</td>
              <td>{{ user.hostname || 'N/A' }}</td>
              <td>{{ user.requested_by }}</td>
              <td>
                <span class="password-display" :title="user.password">
                  {{ user.password ? '••••••••••••••••' : 'N/A' }}
                </span>
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
              <td>
                <span :class="getStatusClass(user.status)">
                  {{ user.status || 'Pending' }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td v-if="canEdit || canDelete" class="action-buttons">
                <button v-if="canEdit" class="btn-action btn-edit" @click="editUser(user)" title="Edit User">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <button v-if="canEdit" class="btn-action btn-tools" @click="offboardingTools(user)" title="Offboarding Tools">
                  <i class="fa-solid fa-gear"></i>
                </button>
                <button v-if="canDelete" class="btn-action btn-delete" @click="deleteUser(user)" title="Delete User">
                  <i class="fa-solid fa-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useAuth } from '../composables/useAuth'

export default {
  name: 'OffboardingView',
  setup() {
    const {
      canCreateUser,
      canEditUser,
      canDeleteUser,
      getCurrentUserEmail,
      getSSOClaims
    } = useAuth()

    return {
      canCreateUser,
      canEditUser,
      canDeleteUser,
      getCurrentUserEmail,
      getSSOClaims
    }
  },
  data() {
    return {
      offboardingData: [],
      loading: false,
      error: null,
      searchQuery: '',
      statusFilter: '',
      recordsPerPage: '25',
      currentPage: 1,
      statusSortOrder: null
    }
  },
  computed: {
    // Use the composable values instead of hardcoded ones
    canCreate() {
      return this.canCreateUser
    },
    canEdit() {
      return this.canEditUser
    },
    canDelete() {
      return this.canDeleteUser
    },
    filteredOffboardingData() {
      let filtered = this.offboardingData

      // Apply search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(user => 
          user.first_name.toLowerCase().includes(query) ||
          user.last_name.toLowerCase().includes(query) ||
          user.company_email.toLowerCase().includes(query) ||
          (user.hostname && user.hostname.toLowerCase().includes(query)) ||
          user.requested_by.toLowerCase().includes(query)
        )
      }

      // Apply status filter
      if (this.statusFilter) {
        filtered = filtered.filter(user => user.status === this.statusFilter)
      }

      // Apply status sorting
      if (this.statusSortOrder) {
        filtered.sort((a, b) => {
          const statusA = a.status || 'Pending'
          const statusB = b.status || 'Pending'
          if (this.statusSortOrder === 'asc') {
            return statusA.localeCompare(statusB)
          } else {
            return statusB.localeCompare(statusA)
          }
        })
      }

      return filtered
    },
    totalRecords() {
      return this.filteredOffboardingData.length
    },
    totalPages() {
      return Math.ceil(this.totalRecords / parseInt(this.recordsPerPage))
    },
    paginatedData() {
      const start = (this.currentPage - 1) * parseInt(this.recordsPerPage)
      const end = start + parseInt(this.recordsPerPage)
      return this.filteredOffboardingData.slice(start, end)
    }
  },
  watch: {
    recordsPerPage() {
      this.currentPage = 1
    },
    searchQuery() {
      this.currentPage = 1
    },
    statusFilter() {
      this.currentPage = 1
    }
  },
  mounted() {
    this.fetchOffboardingData()
  },
  methods: {
    async fetchOffboardingData() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/v1/offboarding/')
        this.offboardingData = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      } catch (error) {
        console.error('Error fetching offboarding data:', error)
        this.error = 'Failed to load offboarding data'
      } finally {
        this.loading = false
      }
    },
    sortByStatus() {
      if (this.statusSortOrder === null) {
        this.statusSortOrder = 'asc'
      } else if (this.statusSortOrder === 'asc') {
        this.statusSortOrder = 'desc'
      } else {
        this.statusSortOrder = null
      }
    },
    clearFilters() {
      this.searchQuery = ''
      this.statusFilter = ''
      this.statusSortOrder = null
      this.currentPage = 1
    },
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
    },
    editUser(user) {
      this.$router.push({
        name: 'edit-offboarding',
        params: { userId: user.id }
      })
    },
    async deleteUser(user) {
      if (confirm(`Are you sure you want to delete the offboarding record for ${user.first_name} ${user.last_name}?`)) {
        try {
          // Get current user email and SSO claims
          const currentUserEmail = this.getCurrentUserEmail()
          const ssoClaimsString = this.getSSOClaims()
          
          const params = new URLSearchParams({
            user_email: currentUserEmail
          })
          
          if (ssoClaimsString) {
            params.append('user_claims', ssoClaimsString)
          }
          
          await axios.delete(`/api/v1/offboarding/${user.id}?${params.toString()}`)
          alert('Offboarding record deleted successfully!')
          await this.fetchOffboardingData()
        } catch (error) {
          console.error('Error deleting offboarding record:', error)
          if (error.response?.status === 403) {
            alert('You do not have permission to delete records. Only administrators can delete offboarding records.')
          } else {
            alert('Error deleting offboarding record: ' + (error.response?.data?.detail || error.message))
          }
        }
      }
    },
    async offboardingTools(user) {
      console.log('offboardingTools called with user:', user)
      // Navigate to the offboarding tools page
      this.$router.push({
        name: 'offboarding-tools',
        params: { userId: user.id }
      })
    },
    getStatusClass(status) {
      const statusMap = {
        'Pending': 'status-pending',
        'In Progress': 'status-in-progress',
        'Completed': 'status-completed',
        'Failed': 'status-failed'
      }
      return statusMap[status] || 'status-pending'
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

    // Authentication and Permission Methods are now handled by the composable
    // Remove the old getCurrentUserEmail method since it's in the composable
  }
}
</script>

<style scoped>
.offboarding-page {
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

.records-per-page label,
.status-filter label {
  font-weight: 500;
  white-space: nowrap;
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

.records-select:focus,
.status-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  min-width: 200px;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.loading-state,
.error-state,
.empty-state {
  padding: 40px;
  text-align: center;
  color: #6b7280;
}

.error-state {
  color: #dc2626;
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
  transform: none;
  box-shadow: none;
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

.data-table th.sortable i {
  margin-left: 4px;
  color: #9ca3af;
  font-size: 0.7rem;
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

.action-column {
  width: 90px;
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.btn-action {
  padding: 2px 4px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.65rem;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 18px;
}

.btn-edit, .btn-tools, .btn-delete {
  border: none;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-size: 0.7rem;
  font-weight: 500;
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

.btn-tools {
  background: #8b5cf6;
  color: white;
  box-shadow: 0 2px 4px rgba(139, 92, 246, 0.3);
}

.btn-tools:hover {
  background: #7c3aed;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(139, 92, 246, 0.4);
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

.status-in-progress {
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

.status-failed {
  background: #fee2e2;
  color: #dc2626;
  padding: 1px 6px;
  border-radius: 8px;
  font-size: 0.65rem;
  font-weight: 500;
}

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

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }

  .data-table {
    font-size: 0.8rem;
  }

  .data-table th,
  .data-table td {
    padding: 8px 6px;
  }
}

/* Password display styles */
.password-display {
  font-family: monospace;
  font-size: 0.9rem;
  color: #6b7280;
  cursor: help;
}

.password-display:hover {
  color: #374151;
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
</style>
