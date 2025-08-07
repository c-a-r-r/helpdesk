<template>
  <div class="onboarding-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>Onboarding Management</h1>
          <p>Manage user onboarding process and records</p>
        </div>
        <router-link v-if="canCreate" to="/onboarding/create" class="btn-primary">
          <i class="fa-solid fa-plus"></i> Add New User
        </router-link>
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
              <th>Ticket #</th>
              <th>Name</th>
              <th>Company Email</th>
              <th>Department</th>
              <th>Title</th>
              <th>Username</th>
              <th class="sortable" @click="sortByStatus">
                Status 
                <i class="fa-solid fa-sort" v-if="!statusSortOrder"></i>
                <i class="fa-solid fa-sort-up" v-if="statusSortOrder === 'asc'"></i>
                <i class="fa-solid fa-sort-down" v-if="statusSortOrder === 'desc'"></i>
              </th>
              <th>Created By</th>
              <th>Start Date</th>
              <th v-if="canEdit || canDelete" class="action-column">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedData" :key="user.id">
              <td>{{ user.ticket_number || 'N/A' }}</td>
              <td>{{ user.first_name }} {{ user.last_name }}</td>
              <td>{{ user.company_email || 'N/A' }}</td>
              <td>{{ user.department }}</td>
              <td>{{ user.title }}</td>
              <td>{{ user.username }}</td>
              <td>
                <span :class="getStatusClass(user.status)">
                  {{ user.status || 'Pending' }}
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
              <td>{{ formatDate(user.start_date) }}</td>
              <td v-if="canEdit || canDelete" class="action-buttons">
                <button v-if="canEdit" class="btn-action btn-edit" @click="editUser(user)" title="Edit User">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <button v-if="canEdit" class="btn-action btn-tools" @click="provisionUser(user)" title="User Management Tools">
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

    <!-- Add/Edit User Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add New User</h3>
          <button class="modal-close" @click="closeModal">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div v-for="(user, index) in users" :key="index" class="user-form-container">
            <div v-if="users.length > 1" class="user-form-header">
              <h3>User {{ index + 1 }}</h3>
              <button type="button" class="btn-remove" @click="removeUser(index)">
                <i class="fa-solid fa-xmark"></i> Remove
              </button>
            </div>
            
            <form class="onboarding-form">
              <div class="form-grid">
                <!-- Status -->
                <div class="form-group">
                  <label :for="'status-' + index">Status</label>
                  <select :id="'status-' + index" v-model="user.status">
                    <option value="Pending">Pending</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                    <option value="Cancelled">Cancelled</option>
                  </select>
                </div>
                
                <!-- Company -->
                <div class="form-group">
                  <label :for="'company-' + index">Company *</label>
                  <input type="text" :id="'company-' + index" v-model="user.company" required
                         placeholder="e.g., Americor">
                </div>
                
                <!-- First Name -->
                <div class="form-group">
                  <label :for="'firstName-' + index">First Name *</label>
                  <input type="text" :id="'firstName-' + index" v-model="user.firstName" required>
                </div>
                
                <!-- Last Name -->
                <div class="form-group">
                  <label :for="'lastName-' + index">Last Name *</label>
                  <input type="text" :id="'lastName-' + index" v-model="user.lastName" required>
                </div>
                
                <!-- Display Name -->
                <div class="form-group">
                  <label :for="'displayName-' + index">Display Name</label>
                  <input type="text" :id="'displayName-' + index" v-model="user.displayName" 
                         placeholder="Auto-generated as First Last" readonly class="readonly-field">
                </div>
                
                <!-- Personal Email -->
                <div class="form-group">
                  <label :for="'personalEmail-' + index">Personal Email *</label>
                  <input type="email" :id="'personalEmail-' + index" v-model="user.personalEmail" required>
                </div>
                
                <!-- Company Email -->
                <div class="form-group">
                  <label :for="'companyEmail-' + index">Company Email</label>
                  <input type="email" :id="'companyEmail-' + index" v-model="user.companyEmail" 
                         placeholder="Auto-generated as username@americor.com" readonly class="readonly-field">
                </div>
                
                <!-- Phone Number -->
                <div class="form-group">
                  <label :for="'phoneNumber-' + index">Phone Number</label>
                  <input type="tel" :id="'phoneNumber-' + index" v-model="user.phoneNumber" 
                         placeholder="555-0000">
                </div>
                
                <!-- Title -->
                <div class="form-group">
                  <label :for="'title-' + index">Title *</label>
                  <input type="text" :id="'title-' + index" v-model="user.title" required>
                </div>
                
                <!-- Manager -->
                <div class="form-group">
                  <label :for="'managerEmail-' + index">Manager's Email *</label>
                  <input type="email" :id="'managerEmail-' + index" v-model="user.managerEmail" required>
                </div>
                
                <!-- Department -->
                <div class="form-group">
                  <label :for="'department-' + index">Department *</label>
                  <select :id="'department-' + index" v-model="user.department" required>
                    <option value="">Select Department</option>
                    <option 
                      v-for="dept in sortedDepartments" 
                      :key="dept.department"
                      :value="dept.department"
                    >
                      {{ dept.department }}
                    </option>
                  </select>
                </div>
                
                <!-- Start Date -->
                <div class="form-group">
                  <label :for="'startDate-' + index">Start Date *</label>
                  <input type="date" :id="'startDate-' + index" v-model="user.startDate" required>
                </div>
                
                <!-- Location First Day -->
                <div class="form-group">
                  <label :for="'locationFirstDay-' + index">Location First Day</label>
                  <input type="text" :id="'locationFirstDay-' + index" v-model="user.locationFirstDay" 
                         placeholder="e.g., Remote">
                </div>
                
                <!-- Username -->
                <div class="form-group">
                  <label :for="'username-' + index">Username</label>
                  <input type="text" :id="'username-' + index" v-model="user.username" 
                         placeholder="Auto-generated as firstname.lastname" readonly class="readonly-field">
                </div>
                
                <!-- Password -->
                <div class="form-group">
                  <label :for="'password-' + index">Password</label>
                  <input type="text" :id="'password-' + index" v-model="user.password" 
                         placeholder="Auto-generated 16-character password" readonly class="readonly-field">
                </div>
                
                <!-- Department OU -->
                <div class="form-group">
                  <label :for="'departmentOU-' + index">Department OU</label>
                  <input 
                    type="text" 
                    :id="'departmentOU-' + index" 
                    v-model="user.departmentOU"
                    readonly
                    :placeholder="user.department ? getDepartmentOU(user.department) || 'OU will be assigned automatically' : 'Select department first'"
                    class="readonly-field"
                  >
                </div>
                
                <!-- Credit9 Alias -->
                <div class="form-group">
                  <label :for="'credit9Alias-' + index">credit9.com Alias</label>
                  <input type="text" :id="'credit9Alias-' + index" v-model="user.credit9Alias" 
                         placeholder="Auto-generated as username@credit9.com" readonly class="readonly-field">
                </div>
                
                <!-- Advantageteam Alias -->
                <div class="form-group">
                  <label :for="'advantageAlias-' + index">advantageteam.law Alias</label>
                  <input type="text" :id="'advantageAlias-' + index" v-model="user.advantageAlias" 
                         placeholder="Auto-generated as username@advantageteam.law" readonly class="readonly-field">
                </div>
                
                <!-- Address Type -->
                <div class="form-group">
                  <label :for="'addressType-' + index">Address Type</label>
                  <select :id="'addressType-' + index" v-model="user.addressType">
                    <option value="Residential">Residential</option>
                    <option value="Commercial">Commercial</option>
                    <option value="PO Box">PO Box</option>
                  </select>
                </div>
                
                <!-- Street Name -->
                <div class="form-group">
                  <label :for="'streetName-' + index">Street Name</label>
                  <input type="text" :id="'streetName-' + index" v-model="user.streetName" 
                         placeholder="123 Main St">
                </div>
                
                <!-- City -->
                <div class="form-group">
                  <label :for="'city-' + index">City</label>
                  <input type="text" :id="'city-' + index" v-model="user.city" 
                         placeholder="City">
                </div>
                
                <!-- State -->
                <div class="form-group">
                  <label :for="'state-' + index">State</label>
                  <input type="text" :id="'state-' + index" v-model="user.state" 
                         placeholder="CA" maxlength="2">
                </div>
                
                <!-- Zip Code -->
                <div class="form-group">
                  <label :for="'zipCode-' + index">Zip Code</label>
                  <input type="text" :id="'zipCode-' + index" v-model="user.zipCode" 
                         placeholder="12345" maxlength="10">
                </div>
                
                <!-- Hostname -->
                <div class="form-group">
                  <label :for="'hostname-' + index">System Hostname</label>
                  <input type="text" :id="'hostname-' + index" v-model="user.hostname" 
                         placeholder="A-XXXXXXXX">
                </div>
                
                <!-- Ticket Number -->
                <div class="form-group">
                  <label :for="'ticketNumber-' + index">Ticket # *</label>
                  <input type="text" :id="'ticketNumber-' + index" v-model="user.ticketNumber" required
                         placeholder="e.g., TKT-2025-001">
                </div>
                
                <!-- Notes -->
                <div class="form-group">
                  <label :for="'notes-' + index">Notes</label>
                  <textarea :id="'notes-' + index" v-model="user.notes" 
                            placeholder="Internal notes..."
                            rows="3"></textarea>
                </div>
                
                <!-- Extra Details -->
                <div class="form-group">
                  <label :for="'extraDetails-' + index">Extra Details</label>
                  <textarea :id="'extraDetails-' + index" v-model="user.extraDetails" 
                            placeholder="Additional notes or special requirements..."
                            rows="3"></textarea>
                </div>
              </div>
            </form>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn-secondary" @click="addAnotherUser">
            <i class="fa-solid fa-plus"></i> Add Another User
          </button>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
            <button type="button" class="btn-primary" @click="submitOnboarding">
              Save User{{ users.length > 1 ? 's' : '' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useDepartmentMappings } from '@/composables/useDepartmentMappings'
import { useAuth } from '@/composables/useAuth'
import axios from 'axios'

export default {
  name: 'OnboardingView',
  setup() {
    const { sortedDepartments, getDepartmentOU } = useDepartmentMappings()
    const {
      canCreateUser,
      canEditUser,
      canDeleteUser,
      getCurrentUserEmail,
      getSSOClaims
    } = useAuth()
    
    return {
      sortedDepartments,
      getDepartmentOU,
      canCreateUser,
      canEditUser,
      canDeleteUser,
      getCurrentUserEmail,
      getSSOClaims
    }
  },
  data() {
    return {
      users: [this.createEmptyUser()],
      onboardingData: [],
      loading: false,
      error: null,
      searchQuery: '',
      statusFilter: '',
      recordsPerPage: 25,
      currentPage: 1,
      statusSortOrder: null, // null, 'asc', 'desc'
      showModal: false
    }
  },
  computed: {
    filteredOnboardingData() {
      // First, filter out any empty or invalid records
      let filtered = this.onboardingData.filter(user => 
        user && user.id && (user.first_name || user.last_name || user.company_email)
      )
      
      // Apply search filter
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
      
      // Apply status filter
      if (this.statusFilter) {
        filtered = filtered.filter(user => 
          (user.status || 'Pending') === this.statusFilter
        )
      }
      
      // Apply status sorting
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
    
    // Authentication and Permission computed properties
    currentUser() {
      return this.getCurrentUser()
    },
    
    isAdmin() {
      return this.canDeleteUser
    },
    
    canEdit() {
      return this.canEditUser
    },
    
    canDelete() {
      return this.canDeleteUser
    },
    
    canCreate() {
      return this.canCreateUser
    }
  },
  mounted() {
    this.fetchOnboardingData()
  },
  watch: {
    users: {
      handler(newUsers) {
        newUsers.forEach(user => {
          // Auto-generate username when first/last name changes
          if (user.firstName && user.lastName) {
            user.username = `${user.firstName.toLowerCase()}.${user.lastName.toLowerCase()}`
            
            // Auto-generate display name
            user.displayName = `${user.firstName} ${user.lastName}`
            
            // Auto-generate company email using the username
            user.companyEmail = `${user.username}@americor.com`
            
            // Auto-populate alias fields using the username
            user.advantageAlias = `${user.username}@advantageteam.law`
            user.credit9Alias = `${user.username}@credit9.com`
          } else {
            // Clear fields when names are not complete
            user.username = ''
            user.displayName = ''
            user.companyEmail = ''
            user.advantageAlias = ''
            user.credit9Alias = ''
          }
          
          // Auto-populate Department OU when department changes
          if (user.department) {
            user.departmentOU = this.getDepartmentOU(user.department)
          } else {
            user.departmentOU = ''
          }
        })
      },
      deep: true
    },
    
    // Reset to page 1 when filters change
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
    showAddUserModal() {
      this.users = [this.createEmptyUser()]
      this.showModal = true
    },

    closeModal() {
      this.showModal = false
      this.users = [this.createEmptyUser()]
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
          // Get current user email and SSO claims
          const currentUserEmail = this.getCurrentUserEmail()
          const ssoClaimsString = this.getSSOClaims()
          
          const params = new URLSearchParams({
            user_email: currentUserEmail
          })
          
          if (ssoClaimsString) {
            params.append('user_claims', ssoClaimsString)
          }
          
          await axios.delete(`/api/v1/onboarding/${user.id}?${params.toString()}`)
          alert('User deleted successfully!')
          await this.fetchOnboardingData()
        } catch (error) {
          console.error('Error deleting user:', error)
          if (error.response?.status === 403) {
            alert('You do not have permission to delete records. Only administrators can delete onboarding records.')
          } else {
            alert('Error deleting user: ' + (error.response?.data?.detail || error.message))
          }
        }
      }
    },

    async provisionUser(user) {
      console.log('provisionUser called with user:', user)
      // Navigate to the user tools page
      this.$router.push({
        name: 'user-tools',
        params: { userId: user.id }
      })
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
    async fetchOnboardingData() {
      this.loading = true
      this.error = null
      
      try {
        console.log('Fetching onboarding data from API...')
        const response = await axios.get('/api/v1/onboarding/')
        console.log('API Response:', response.data)
        console.log('Response type:', typeof response.data)
        console.log('Is array:', Array.isArray(response.data))
        
        // Ensure response.data is an array
        let rawData = response.data
        if (!Array.isArray(rawData)) {
          console.warn('API response is not an array, trying to handle it...')
          // If it's an object with a data property, use that
          if (rawData && rawData.data && Array.isArray(rawData.data)) {
            rawData = rawData.data
          } else {
            // If it's a single object, wrap it in an array
            rawData = rawData ? [rawData] : []
          }
        }
        
        console.log('Raw data length:', rawData.length)
        
        // Ensure we only get valid records
        const validData = rawData.filter(user => 
          user && user.id && (user.first_name || user.last_name || user.company_email)
        )
        
        // Sort by id in descending order - newest records (higher IDs) first
        const sortedData = validData.sort((a, b) => {
          return b.id - a.id // Descending order (newest first)
        })
        
        this.onboardingData = sortedData
        console.log(`Loaded ${this.onboardingData.length} valid onboarding records`)
        console.log('Valid records:', this.onboardingData)
      } catch (error) {
        console.error('Error fetching onboarding data:', error)
        this.error = error.response?.data?.detail || error.message || 'Failed to fetch data'
      } finally {
        this.loading = false
      }
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
    
    createEmptyUser() {
      const user = {
        ticketNumber: '',
        firstName: '',
        lastName: '',
        displayName: '',
        personalEmail: '',
        companyEmail: '',
        phoneNumber: '',
        title: '',
        managerEmail: '',
        department: '',
        startDate: new Date().toISOString().split('T')[0], // Default to today
        status: 'Pending',
        locationFirstDay: '',
        username: '',
        password: '',
        departmentOU: '',
        credit9Alias: '',
        advantageAlias: '',
        addressType: 'Residential',
        streetName: '',
        city: '',
        state: '',
        zipCode: '',
        hostname: '',
        notes: '',
        extraDetails: '',
        company: ''
      }
      // Auto-generate password immediately
      user.password = this.generatePassword()
      return user
    },
    
    addAnotherUser() {
      this.users.push(this.createEmptyUser())
    },
    
    removeUser(index) {
      if (this.users.length > 1) {
        this.users.splice(index, 1)
      }
    },
    
    generatePassword() {
      const chars = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$%^&*'
      let password = ''
      for (let i = 0; i < 16; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length))
      }
      return password
    },
    
    async submitOnboarding() {
      // Auto-generate missing fields
      this.users.forEach((user) => {
        if (!user.username && user.firstName && user.lastName) {
          user.username = `${user.firstName.toLowerCase()}.${user.lastName.toLowerCase()}`
        }
        if (!user.displayName && user.firstName && user.lastName) {
          user.displayName = `${user.firstName} ${user.lastName}`
        }
        if (!user.companyEmail && user.username) {
          user.companyEmail = `${user.username}@americor.com`
        }
        if (!user.advantageAlias && user.username) {
          user.advantageAlias = `${user.username}@advantageteam.law`
        }
        if (!user.credit9Alias && user.username) {
          user.credit9Alias = `${user.username}@credit9.com`
        }
        if (!user.departmentOU && user.department) {
          user.departmentOU = this.getDepartmentOU(user.department)
        }
        // Always generate a fresh 16-character password for new users
        if (!user.password) {
          user.password = this.generatePassword()
        }
        // Set default values for missing fields
        if (!user.company || user.company.trim() === '') {
          user.company = 'Americor'
        }
        if (!user.phoneNumber) {
          user.phoneNumber = '555-0000'
        }
        if (!user.addressType) {
          user.addressType = 'Residential'
        }
        if (!user.streetName) {
          user.streetName = '123 Main St'
        }
        if (!user.city) {
          user.city = 'City'
        }
        if (!user.state) {
          user.state = 'CA'
        }
        if (!user.zipCode) {
          user.zipCode = '12345'
        }
      })
      
      try {
        // Get current user email for created_by tracking
        const currentUserEmail = this.getCurrentUserEmail()
        
        // Create new users
        for (const user of this.users) {
          const onboardingData = {
            company: user.company || 'Americor',
            first_name: user.firstName,
            last_name: user.lastName,
            display_name: user.displayName || `${user.firstName} ${user.lastName}`,
            personal_email: user.personalEmail,
            company_email: user.companyEmail,
            phone_number: user.phoneNumber ? String(user.phoneNumber) : '555-0000',
            title: user.title,
            manager: user.managerEmail,
            department: user.department,
            start_date: user.startDate ? new Date(user.startDate).toISOString() : new Date().toISOString(),
            status: user.status || 'Pending',
            location_first_day: user.locationFirstDay || null,
            username: user.username,
            password: user.password,
            department_ou: user.departmentOU,
            credit9_alias: user.credit9Alias,
            advantageteam_alias: user.advantageAlias,
            address_type: user.addressType || 'Residential',
            street_name: user.streetName || '123 Main St',
            city: user.city || 'City',
            state: user.state || 'CA',
            zip_code: user.zipCode ? String(user.zipCode) : '12345',
            hostname: user.hostname,
            ticket_number: user.ticketNumber ? String(user.ticketNumber) : null,
            notes: user.notes || null,
            extra_details: user.extraDetails || null
          }
          
          console.log('Saving new user:', onboardingData)
          await axios.post(`/api/v1/onboarding/?user_email=${encodeURIComponent(currentUserEmail)}`, onboardingData)
        }
        alert(`Successfully onboarded ${this.users.length} user(s)!`)
        
        this.closeModal()
        await this.fetchOnboardingData()
      } catch (error) {
        console.error('Error saving onboarding data:', error)
        // Better error handling to show actual validation errors
        if (error.response?.data?.detail) {
          if (Array.isArray(error.response.data.detail)) {
            const errors = error.response.data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join('\n')
            alert('Validation errors:\n' + errors)
          } else {
            alert('Error: ' + error.response.data.detail)
          }
        } else {
          alert('Error saving onboarding data: ' + error.message)
        }
      }
    },
    
    resetForm() {
      this.users = [this.createEmptyUser()]
    },

    // Authentication and Permission Methods
    getCurrentUserEmail() {
      // Try to get user data from JumpCloud SSO claims in sessionStorage
      const userClaims = sessionStorage.getItem('userClaims')
      if (userClaims) {
        try {
          const claims = JSON.parse(userClaims)
          console.log('JumpCloud SSO claims received:', claims)
          
          // Try to get email from JumpCloud claims
          if (claims.email) {
            const email = Array.isArray(claims.email) ? claims.email[0] : claims.email
            console.log('Found email in claims:', email)
            return email
          }
          
          // Try preferred_username
          if (claims.preferred_username && claims.preferred_username.includes('@')) {
            const email = Array.isArray(claims.preferred_username) ? claims.preferred_username[0] : claims.preferred_username
            console.log('Found email in preferred_username:', email)
            return email
          }
          
          // If no direct email, construct one from name fields
          if (claims.given_name && claims.family_name) {
            const firstName = Array.isArray(claims.given_name) ? claims.given_name[0] : claims.given_name
            const lastName = Array.isArray(claims.family_name) ? claims.family_name[0] : claims.family_name
            const constructedEmail = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@americor.com`
            console.log('Constructed email from name:', constructedEmail)
            return constructedEmail
          }
          
        } catch (error) {
          console.error('Error parsing JumpCloud SSO claims:', error)
        }
      }
      
      // Check localStorage for any user tokens
      const userToken = localStorage.getItem('userToken')
      if (userToken) {
        try {
          const tokenParts = userToken.split('.')
          if (tokenParts.length === 3) {
            const payload = JSON.parse(atob(tokenParts[1]))
            if (payload.email) {
              const email = Array.isArray(payload.email) ? payload.email[0] : payload.email
              console.log('Found email in JWT token:', email)
              return email
            }
            if (payload.preferred_username && payload.preferred_username.includes('@')) {
              const email = Array.isArray(payload.preferred_username) ? payload.preferred_username[0] : payload.preferred_username
              console.log('Found email in JWT preferred_username:', email)
              return email
            }
          }
        } catch (error) {
          console.error('Error decoding JWT token:', error)
        }
      }
      
      // If we're in development and the current user is cristian.rodriguez
      if (process.env.NODE_ENV === 'development') {
        console.warn('Development mode: using cristian.rodriguez@americor.com')
        return 'cristian.rodriguez@americor.com'
      }
      
      // No authentication found
      throw new Error('User not authenticated via SSO')
    },

    getCurrentUser() {
      // Get full user information from SSO claims
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
      
      // Development fallback
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
      
      // Combine groups and role attribute
      let allRoles = Array.isArray(groups) ? [...groups] : [groups]
      if (roleAttribute) {
        if (Array.isArray(roleAttribute)) {
          allRoles = allRoles.concat(roleAttribute)
        } else {
          allRoles.push(roleAttribute)
        }
      }
      
      // Check for exact role matches from SAML Role attribute
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
    }
  }
}
</script>

<style scoped>
.onboarding-page {
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

.form-content {
  padding: 20px;
}

/* Multi-User Form Styles */
.user-form-container {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background: #f9fafb;
}

.user-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.user-form-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.2rem;
}

.btn-remove {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #dc2626;
  border: 2px solid #fecaca;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-remove:hover {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  border-color: #f87171;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(220, 38, 38, 0.2);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 4px;
  color: #374151;
  font-weight: 500;
  font-size: 0.85rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
  background: white;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 60px;
}

.readonly-field {
  background-color: #f9fafb !important;
  color: #6b7280 !important;
  cursor: not-allowed;
}

.readonly-field::placeholder {
  color: #9ca3af;
  font-style: italic;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  border-top: 1px solid #e5e7eb;
  padding-top: 16px;
  margin-top: 16px;
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

.btn-primary:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
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
  padding: 4px 4px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.6rem;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
}

.btn-edit {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1d4ed8;
  border: 1px solid #93c5fd;
}

.btn-edit:hover {
  background: linear-gradient(135deg, #bfdbfe 0%, #93c5fd 100%);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(29, 78, 216, 0.2);
}

.btn-tools {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  border: 1px solid #fbbf24;
}

.btn-tools:hover {
  background: linear-gradient(135deg, #fde68a 0%, #fbbf24 100%);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(217, 119, 6, 0.2);
}

.btn-delete {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #dc2626;
  border: 1px solid #fecaca;
}

.btn-delete:hover {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(220, 38, 38, 0.2);
}

/* Status badges */
.status-pending {
  background: #fef3c7;
  color: #d97706;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-progress {
  background: #dbeafe;
  color: #1d4ed8;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-cancelled {
  background: #fee2e2;
  color: #dc2626;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
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

.modal-close {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  font-size: 1.2rem;
  cursor: pointer;
  color: #64748b;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.modal-close:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #475569;
  transform: scale(1.05);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

/* Responsive adjustments */
@media (max-width: 1400px) {
  .form-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1024px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .user-form-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .modal-overlay {
    padding: 10px;
  }

  .modal-content {
    max-height: 95vh;
  }

  .modal-body {
    padding: 16px;
  }

  .modal-header {
    padding: 16px;
  }

  .modal-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .modal-actions {
    flex-direction: column;
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

/* Tools Modal Specific Styles */
.tools-modal {
  max-width: 1200px;
  width: 95vw;
  max-height: 95vh;
  padding: 0;
  border-radius: 12px;
  overflow: hidden;
}

.tools-modal .modal-content {
  padding: 0;
}

/* Full Screen CreateUser Styles */
.create-user-fullscreen {
  position: relative;
  min-height: 100vh;
  background: #f8fafc;
  padding: 20px;
}

.btn-back {
  position: absolute;
  top: 20px;
  right: 20px;
  background: #64748b;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  z-index: 10;
}

.btn-back:hover {
  background: #475569;
  transform: translateY(-1px);
}

.btn-back i {
  font-size: 12px;
}

/* Password field styling */
.password-field {
  font-family: monospace;
  font-size: 0.7rem;
  color: #6b7280;
  background: #f9fafb;
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid #e5e7eb;
  cursor: help;
}

.password-field:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}
</style>
