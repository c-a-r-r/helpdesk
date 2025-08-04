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
        <table class="credential-table">
          <thead>
            <tr>
              <th class="credential-title">Credential Sheet</th>
              <th class="employee-name">{{ selectedUser.firstName }} {{ selectedUser.lastName }}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colspan="2" class="section-title-full">Email Address</td>
            </tr>
            <tr>
              <td colspan="2" class="credential-item">{{ selectedUser.companyEmail }}</td>
            </tr>
            
            <tr>
              <td class="section-title">Windows & Jumpcloud</td>
              <td class="section-title">Google</td>
            </tr>
            <tr>
              <td class="credential-cell">
                <table class="credential-subtable">
                  <tr>
                    <td class="credential-label">Username</td>
                    <td class="credential-value">{{ selectedUser.companyEmail }}</td>
                  </tr>
                  <tr>
                    <td class="credential-label">Password</td>
                    <td class="credential-value">{{ selectedUser.password }}</td>
                  </tr>
                </table>
              </td>
              <td class="credential-cell">
                <table class="credential-subtable">
                  <tr>
                    <td class="credential-label">Username</td>
                    <td class="credential-value">{{ selectedUser.companyEmail }}</td>
                  </tr>
                  <tr>
                    <td class="credential-label">Password</td>
                    <td class="credential-value">Use SSO (single sign-on) with Jumpcloud</td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <tr v-if="selectedUser.zoom || selectedUser.five9">
              <td class="section-title" v-if="selectedUser.zoom">Zoom</td>
              <td class="section-title" v-if="selectedUser.five9">Five9</td>
              <td class="section-title" v-if="!selectedUser.zoom && selectedUser.five9">CRM SIGN IN VIA GOOGLE</td>
              <td class="section-title" v-if="selectedUser.zoom && !selectedUser.five9">CRM SIGN IN VIA GOOGLE</td>
            </tr>
            <tr v-if="selectedUser.zoom || selectedUser.five9">
              <td class="credential-cell" v-if="selectedUser.zoom">
                <table class="credential-subtable">
                  <tr>
                    <td class="credential-label">Username</td>
                    <td class="credential-value">{{ selectedUser.companyEmail }}</td>
                  </tr>
                  <tr>
                    <td class="credential-label">Password</td>
                    <td class="credential-value">Use SSO (single sign-on) with Jumpcloud</td>
                  </tr>
                </table>
              </td>
              <td class="credential-cell" v-if="selectedUser.five9">
                <table class="credential-subtable">
                  <tr>
                    <td class="credential-label">Username</td>
                    <td class="credential-value">{{ selectedUser.companyEmail }}</td>
                  </tr>
                  <tr>
                    <td class="credential-label">Password</td>
                    <td class="credential-value">Use SSO (single sign-on) with Jumpcloud</td>
                  </tr>
                  <tr>
                    <td class="credential-label">Extension</td>
                    <td class="credential-value">{{ selectedUser.extension || 'To be assigned' }}</td>
                  </tr>
                </table>
              </td>
              <td class="credential-cell" v-if="!selectedUser.zoom && selectedUser.five9">
                <table class="credential-subtable">
                  <tr>
                    <td class="credential-label">Username</td>
                    <td class="credential-value">{{ selectedUser.companyEmail }}</td>
                  </tr>
                  <tr>
                    <td class="credential-label">Password</td>
                    <td class="credential-value">Use SSO (single sign-on) with Jumpcloud</td>
                  </tr>
                  <tr>
                    <td class="credential-label">&nbsp;</td>
                    <td class="credential-value">&nbsp;</td>
                  </tr>
                </table>
              </td>
              <td class="credential-cell" v-if="selectedUser.zoom && !selectedUser.five9">
                <table class="credential-subtable">
                  <tr>
                    <td class="credential-label">Username</td>
                    <td class="credential-value">{{ selectedUser.companyEmail }}</td>
                  </tr>
                  <tr>
                    <td class="credential-label">Password</td>
                    <td class="credential-value">Use SSO (single sign-on) with Jumpcloud</td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <tr v-if="!selectedUser.zoom && !selectedUser.five9">
              <td colspan="2" class="section-title-full">CRM SIGN IN VIA GOOGLE</td>
            </tr>
            <tr v-if="!selectedUser.zoom && !selectedUser.five9">
              <td colspan="2" class="credential-cell">
                <table class="credential-subtable">
                  <tr>
                    <td class="credential-label">Username</td>
                    <td class="credential-value">{{ selectedUser.companyEmail }}</td>
                  </tr>
                  <tr>
                    <td class="credential-label">Password</td>
                    <td class="credential-value">Use SSO (single sign-on) with Jumpcloud</td>
                  </tr>
                </table>
              </td>
            </tr>
          </tbody>
        </table>
        
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
        })).sort((a, b) => b.id - a.id) // Sort by ID descending (newest first)
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
      // Add print class to body to override any external styles
      document.body.classList.add('printing')
      
      // Hide any potential overlays or highlights
      const overlaySelectors = [
        '[class*="highlight"]',
        '[class*="annotation"]', 
        '[class*="overlay"]',
        '[style*="pink"]',
        '[style*="magenta"]'
      ]
      
      const overlays = []
      overlaySelectors.forEach(selector => {
        const elements = document.querySelectorAll(selector)
        elements.forEach(el => {
          overlays.push({element: el, originalDisplay: el.style.display})
          el.style.display = 'none'
        })
      })
      
      // Use browser's native print
      window.print()
      
      // Restore elements after print
      setTimeout(() => {
        document.body.classList.remove('printing')
        overlays.forEach(({element, originalDisplay}) => {
          element.style.display = originalDisplay
        })
      }, 1000)
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
  font-family: Arial, sans-serif;
}

.credential-table {
  width: 100%;
  border-collapse: collapse;
  border: 4px solid #000;
  background: white;
  table-layout: fixed;
  font-family: Arial, sans-serif;
}

.credential-table th,
.credential-table td {
  border: 2px solid #000;
  padding: 0;
  margin: 0;
  vertical-align: middle;
}

.credential-title {
  background: #f0f0f0 !important;
  padding: 15px;
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  width: 50%;
  height: 60px;
  vertical-align: middle;
  border: 2px solid #000;
}

.employee-name {
  background: #e6f3ff !important;
  padding: 15px;
  font-size: 22px;
  font-weight: bold;
  text-align: center;
  width: 50%;
  height: 60px;
  vertical-align: middle;
  border: 2px solid #000;
}

.section-title {
  background: #f8f8f8 !important;
  padding: 12px;
  font-weight: bold;
  text-align: center;
  font-size: 16px;
  height: 40px;
  vertical-align: middle;
  border: 2px solid #000;
}

.section-title-full {
  background: #f8f8f8 !important;
  padding: 12px;
  font-weight: bold;
  text-align: center;
  font-size: 16px;
  height: 40px;
  vertical-align: middle;
  border: 2px solid #000;
}

.credential-item {
  padding: 12px;
  text-align: center;
  font-weight: bold;
  font-size: 18px;
  height: 40px;
  vertical-align: middle;
  border: 2px solid #000;
}

.credential-cell {
  padding: 0;
  vertical-align: middle;
  border: 2px solid #000 !important;
  height: auto;
  position: relative;
}

.credential-subtable {
  width: 100%;
  border-collapse: collapse;
  border: none;
  margin: 0;
  padding: 0;
}

.credential-subtable tr {
  border: none;
  margin: 0;
  padding: 0;
}

.credential-subtable td {
  margin: 0;
  padding: 0;
  border: none;
  border-bottom: 2px solid #000;
  vertical-align: middle;
  height: 50px;
}

.credential-subtable tr:last-child td {
  border-bottom: none;
}

.credential-label {
  padding: 10px 15px;
  background: #f8f8f8 !important;
  font-weight: bold;
  border-right: 2px solid #000 !important;
  width: 33.33%;
  text-align: center;
  font-size: 14px;
  min-height: 50px;
}

.credential-value {
  padding: 10px 15px;
  background: white !important;
  width: 66.67%;
  text-align: center;
  font-size: 14px;
  word-break: break-word;
  min-height: 50px;
}

.credential-footer {
  border: 4px solid #000;
  border-top: 2px solid #000;
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin-top: -2px;
}

.setup-instructions {
  padding: 20px;
  border-right: 2px solid #000;
  background: white;
}

.instruction-title {
  font-weight: bold;
  margin-bottom: 12px;
  text-decoration: underline;
  font-size: 16px;
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
  background: white;
}

.contact-title {
  font-weight: bold;
  margin-bottom: 15px;
  font-size: 18px;
}

.contact-details {
  font-size: 20px;
  font-weight: bold;
  line-height: 1.6;
}

.policy-note {
  grid-column: 1 / -1;
  padding: 15px;
  border-top: 2px solid #000;
  font-size: 12px;
  text-align: center;
  background: #f9f9f9 !important;
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

/* Hide overlays when printing class is active */
body.printing *[class*="highlight"],
body.printing *[class*="annotation"],
body.printing *[class*="overlay"],
body.printing *[style*="pink"],
body.printing *[style*="magenta"] {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
}

@media print {
  /* Hide everything except credential sheet */
  body * {
    visibility: hidden;
  }
  
  .credential-sheet,
  .credential-sheet * {
    visibility: visible;
  }
  
  /* Hide scrollbars and buttons */
  body {
    overflow: hidden !important;
  }
  
  /* Hide all buttons and interactive elements */
  button,
  .btn-primary,
  .btn-outline,
  input,
  .search-box,
  .section-header,
  .page-header,
  .content-section:first-child {
    visibility: hidden !important;
    display: none !important;
  }
  
  .credential-sheet {
    position: absolute;
    left: 0;
    top: 0;
    width: 100% !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 0 !important;
    z-index: 9999 !important;
    overflow: visible !important;
  }
  
  /* Hide any overlays, highlights, annotations, or visual aids */
  *[style*="pink"],
  *[style*="magenta"],
  *[style*="#ff69b4"],
  *[style*="#ffc0cb"],
  *[style*="rgba(255"],
  *[class*="highlight"],
  *[class*="annotation"],
  *[class*="overlay"],
  *[class*="tooltip"],
  *[class*="popup"],
  .pink,
  .highlight,
  .annotation,
  .overlay,
  .tooltip,
  .popup {
    visibility: hidden !important;
    display: none !important;
    opacity: 0 !important;
  }
  
  /* Remove any colored borders or backgrounds */
  * {
    border-color: #000 !important;
    outline: none !important;
    box-shadow: none !important;
    text-shadow: none !important;
  }
  
  /* Override any inspector/developer tool styles */
  *::before,
  *::after {
    display: none !important;
    content: none !important;
  }
  
  /* Force all borders to be complete and consistent */
  .credential-table {
    border: 4px solid #000 !important;
    border-collapse: collapse !important;
    width: 100% !important;
  }
  
  .credential-table th,
  .credential-table td {
    border: 2px solid #000 !important;
    padding: 0 !important;
    margin: 0 !important;
    vertical-align: middle !important;
  }
  
  .credential-cell {
    border: 2px solid #000 !important;
    padding: 0 !important;
    vertical-align: middle !important;
  }
  
  .credential-subtable {
    width: 100% !important;
    border-collapse: collapse !important;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  
  .credential-subtable tr {
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  
  .credential-subtable td {
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    border-bottom: 2px solid #000 !important;
    vertical-align: middle !important;
    height: 45px !important;
  }
  
  .credential-subtable tr:last-child td {
    border-bottom: none !important;
  }
  
  .credential-label {
    border-right: 2px solid #000 !important;
    background: #f8f8f8 !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    padding: 10px 12px !important;
    width: 33.33% !important;
    text-align: center !important;
    font-size: 12px !important;
    min-height: 45px !important;
    font-weight: bold !important;
  }
  
  .credential-value {
    background: white !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    padding: 10px 12px !important;
    width: 66.67% !important;
    text-align: center !important;
    font-size: 12px !important;
    min-height: 45px !important;
  }
  
  .credential-title {
    background: #f0f0f0 !important;
    border: 2px solid #000 !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  
  .employee-name {
    background: #e6f3ff !important;
    border: 2px solid #000 !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  
  .section-title,
  .section-title-full {
    background: #f8f8f8 !important;
    border: 2px solid #000 !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  
  .credential-item {
    border: 2px solid #000 !important;
  }
  
  .credential-footer {
    border: 4px solid #000 !important;
    border-top: 2px solid #000 !important;
  }
  
  .setup-instructions {
    border-right: 2px solid #000 !important;
  }
  
  .policy-note {
    border-top: 2px solid #000 !important;
    background: #f9f9f9 !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}
</style>
