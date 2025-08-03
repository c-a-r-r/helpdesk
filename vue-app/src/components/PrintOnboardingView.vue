<template>
  <div class="print-onboarding-page">
    <div class="page-header">
      <h1>Print Onboarding Information</h1>
      <p>Generate and print onboarding documentation for employees</p>
    </div>

    <div class="content-section">
      <div class="section-header">
        <h2>Select User</h2>
      </div>
      
      <div class="search-content">
        <div v-if="loading" class="loading-state">
          <p>Loading onboarding records...</p>
        </div>
        
        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
          <button class="btn-outline" @click="loadUsers">Try Again</button>
        </div>
        
        <div v-else>
          <div class="search-box">
            <input 
              type="text" 
              placeholder="Search by name or email..." 
              v-model="searchQuery"
              @input="filterUsers"
            >
            <button class="search-btn">🔍</button>
          </div>
          
          <div class="users-list">
            <div v-if="filteredUsers.length === 0" class="no-results">
              <p>No users found matching your search.</p>
            </div>
            <div 
              v-for="user in filteredUsers" 
              :key="user.id" 
              class="user-item"
              :class="{ selected: selectedUser?.id === user.id }"
              @click="selectUser(user)"
            >
              <div class="user-info">
                <div class="user-name">{{ user.firstName }} {{ user.lastName }}</div>
                <div class="user-details">{{ user.companyEmail }} • {{ user.department }}</div>
              </div>
              <div class="user-status" :class="user.status.toLowerCase()">{{ user.status }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedUser" class="content-section">
      <div class="section-header">
        <h2>Credential Sheet for {{ selectedUser.firstName }} {{ selectedUser.lastName }}</h2>
        <button class="btn-primary" @click="printInfo">🖨️ Print Credential Sheet</button>
      </div>
      
      <div class="credential-sheet" ref="printableContent">
        <div class="credential-header">
          <div class="credential-title">Credential Sheet</div>
          <div class="employee-name">{{ selectedUser.firstName }} {{ selectedUser.lastName }}</div>
        </div>
        
        <div class="credential-content">
          <div class="credential-section">
            <div class="section-title">Email Address</div>
            <div class="credential-item">
              <span class="credential-value">{{ selectedUser.companyEmail }}</span>
            </div>
          </div>
          
          <div class="credential-section">
            <div class="section-title">Windows & Jumpcloud</div>
            <div class="credential-row">
              <span class="credential-label">Username</span>
              <span class="credential-value">{{ selectedUser.companyEmail }}</span>
            </div>
            <div class="credential-row">
              <span class="credential-label">Password</span>
              <span class="credential-value">{{ selectedUser.password }}</span>
            </div>
          </div>
          
          <div class="credential-section">
            <div class="section-title">Google</div>
            <div class="credential-row">
              <span class="credential-label">Username</span>
              <span class="credential-value">{{ selectedUser.companyEmail }}</span>
            </div>
            <div class="credential-row">
              <span class="credential-label">Password</span>
              <span class="credential-value">Use SSO (single sign-on) with Jumpcloud</span>
            </div>
          </div>
          
          <div v-if="selectedUser.zoom" class="credential-section">
            <div class="section-title">Zoom</div>
            <div class="credential-row">
              <span class="credential-label">Username</span>
              <span class="credential-value">{{ selectedUser.companyEmail }}</span>
            </div>
            <div class="credential-row">
              <span class="credential-label">Password</span>
              <span class="credential-value">Use SSO (single sign-on) with Jumpcloud</span>
            </div>
            <div class="credential-row">
              <span class="credential-label">Phone Number</span>
              <span class="credential-value">{{ selectedUser.phoneNumber || 'N/A' }}</span>
            </div>
            <div class="credential-row">
              <span class="credential-label">Station ID</span>
              <span class="credential-value">Not Required For Zoom</span>
            </div>
          </div>
          
          <div v-if="selectedUser.five9" class="credential-section">
            <div class="section-title">Five9</div>
            <div class="credential-row">
              <span class="credential-label">Username</span>
              <span class="credential-value">{{ selectedUser.companyEmail }}</span>
            </div>
            <div class="credential-row">
              <span class="credential-label">Password</span>
              <span class="credential-value">Use SSO (single sign-on) with Jumpcloud</span>
            </div>
            <div class="credential-row">
              <span class="credential-label">Extension</span>
              <span class="credential-value">{{ selectedUser.extension || 'To be assigned' }}</span>
            </div>
          </div>
          
          <div class="credential-section">
            <div class="section-title">CRM SIGN IN VIA GOOGLE</div>
            <div class="credential-row">
              <span class="credential-label">Username</span>
              <span class="credential-value">{{ selectedUser.companyEmail }}</span>
            </div>
            <div class="credential-row">
              <span class="credential-label">Password</span>
              <span class="credential-value">Use SSO (single sign-on) with Jumpcloud</span>
            </div>
          </div>
        </div>
        
        <div class="credential-footer">
          <div class="setup-instructions">
            <div class="instruction-title">First Time Setup (2FA and Password Reset):</div>
            <div class="instruction-steps">
              <div class="instruction-step">1. In Google Chrome go to Americor Bookmarks > JumpCloud Portal</div>
              <div class="instruction-step">2. Log in using your Windows & Jumpcloud email and password.</div>
              <div class="instruction-step">3. On the left side, go to Security > Enroll device in JumpCloud Protect. Follow the instructions to install JumpCloud Protect on your phone.</div>
              <div class="instruction-step">4. After enrolling your device, click on "Reset Password" in the Security tab and follow the directions.</div>
              <div class="instruction-step">5. You are done!</div>
            </div>
          </div>
          
          <div class="contact-info">
            <div class="contact-title">For IT inquiries please email or call:</div>
            <div class="contact-details">
              <div>helpdesk@americor.com</div>
              <div>833-654-2247</div>
            </div>
          </div>
          
          <div class="policy-note">
            <strong>Remote Work Equipment & Monitoring Policy</strong><br>
            Company equipment is for work use only and must be returned when requested. Company systems may be monitored. There is no expectation of privacy. Please refer to the company handbook.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'PrintOnboardingView',
  data() {
    return {
      searchQuery: '',
      selectedUser: null,
      users: [],
      filteredUsers: [],
      loading: false,
      error: null
    }
  },
  mounted() {
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/v1/onboarding/')
        this.users = response.data.map(user => ({
          id: user.id,
          firstName: user.first_name || '',
          lastName: user.last_name || '',
          displayName: user.display_name || `${user.first_name} ${user.last_name}`,
          email: user.personal_email || '',
          companyEmail: user.company_email || '',
          department: user.department || '',
          title: user.title || '',
          username: user.username || '',
          password: user.password || '',
          startDate: user.start_date ? new Date(user.start_date) : null,
          status: user.status || 'pending',
          company: user.company || '',
          manager: user.manager || '',
          phoneNumber: user.phone_number || '',
          ticketNumber: user.ticket_number || '',
          zoom: user.zoom || false,
          five9: user.five9 || false,
          extension: user.extension || null
        }))
        this.filteredUsers = this.users
      } catch (error) {
        console.error('Error loading users:', error)
        this.error = 'Failed to load onboarding records'
      } finally {
        this.loading = false
      }
    },
    filterUsers() {
      if (!this.searchQuery) {
        this.filteredUsers = this.users
        return
      }
      
      const query = this.searchQuery.toLowerCase()
      this.filteredUsers = this.users.filter(user => 
        user.firstName.toLowerCase().includes(query) ||
        user.lastName.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query) ||
        user.companyEmail.toLowerCase().includes(query)
      )
    },
    selectUser(user) {
      this.selectedUser = user
    },
    printInfo() {
      window.print()
    },
    formatDate(date) {
      if (!date) return 'N/A'
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }).format(date)
    }
  }
}
</script>

<style scoped>
.print-onboarding-page {
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

.search-content {
  padding: 30px;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 20px;
  max-width: 400px;
}

.search-box input {
  border: none;
  background: none;
  outline: none;
  padding: 4px 8px;
  flex: 1;
}

.search-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.users-list {
  max-height: 300px;
  overflow-y: auto;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-item:hover {
  background: #f9fafb;
  border-color: #667eea;
}

.user-item.selected {
  background: #eff6ff;
  border-color: #667eea;
}

.user-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.user-details {
  color: #6b7280;
  font-size: 0.9rem;
}

.user-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.user-status.active {
  background: #f0fdf4;
  color: #16a34a;
}

.user-status.pending {
  background: #fef3c7;
  color: #d97706;
}

.loading-state,
.error-state {
  padding: 40px;
  text-align: center;
  color: #6b7280;
}

.error-state {
  color: #dc2626;
}

.no-results {
  padding: 20px;
  text-align: center;
  color: #6b7280;
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

/* Credential Sheet Styles */
.credential-sheet {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border: 2px solid #000;
  font-family: Arial, sans-serif;
}

.credential-header {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-bottom: 2px solid #000;
}

.credential-title {
  background: #f0f0f0;
  padding: 20px;
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  border-right: 2px solid #000;
}

.employee-name {
  background: #e6f3ff;
  padding: 20px;
  font-size: 20px;
  font-weight: bold;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.credential-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.credential-section {
  border-bottom: 1px solid #000;
  border-right: 1px solid #000;
}

.credential-section:nth-child(even) {
  border-right: none;
}

.credential-section:last-child,
.credential-section:nth-last-child(2) {
  border-bottom: none;
}

.section-title {
  background: #f0f0f0;
  padding: 12px;
  font-weight: bold;
  text-align: center;
  border-bottom: 1px solid #000;
}

.credential-item {
  padding: 12px;
  text-align: center;
  font-weight: bold;
}

.credential-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  border-bottom: 1px solid #ddd;
}

.credential-row:last-child {
  border-bottom: none;
}

.credential-label {
  padding: 8px 12px;
  background: #f8f8f8;
  font-weight: bold;
  border-right: 1px solid #ddd;
}

.credential-value {
  padding: 8px 12px;
  background: white;
}

.credential-footer {
  border-top: 2px solid #000;
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.setup-instructions {
  padding: 20px;
  border-right: 2px solid #000;
}

.instruction-title {
  font-weight: bold;
  margin-bottom: 10px;
  text-decoration: underline;
}

.instruction-steps {
  font-size: 12px;
  line-height: 1.4;
}

.instruction-step {
  margin-bottom: 8px;
}

.contact-info {
  padding: 20px;
  text-align: center;
}

.contact-title {
  font-weight: bold;
  margin-bottom: 15px;
  font-size: 16px;
}

.contact-details {
  font-size: 18px;
  font-weight: bold;
  line-height: 1.5;
}

.policy-note {
  grid-column: 1 / -1;
  padding: 15px;
  border-top: 1px solid #000;
  font-size: 10px;
  text-align: center;
  background: #f9f9f9;
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

@media print {
  .page-header,
  .search-content,
  .section-header {
    display: none !important;
  }
  
  .content-section {
    box-shadow: none;
    border: none;
    margin: 0;
    padding: 0;
  }
  
  .credential-sheet {
    margin: 0;
    max-width: none;
    width: 100%;
    font-size: 12px;
  }
  
  .credential-title {
    font-size: 20px;
  }
  
  .employee-name {
    font-size: 18px;
  }
  
  .contact-title {
    font-size: 14px;
  }
  
  .contact-details {
    font-size: 16px;
  }
  
  .instruction-steps {
    font-size: 10px;
  }
  
  .policy-note {
    font-size: 8px;
  }
  
  /* Ensure proper page breaks */
  .credential-sheet {
    page-break-inside: avoid;
  }
}
</style>
