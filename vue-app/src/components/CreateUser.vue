<template>
  <div class="create-user-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>Create New User</h1>
          <p>Add a new user to the onboarding system</p>
        </div>
        <button class="btn-secondary" @click="goBack">
          <i class="fa-solid fa-arrow-left"></i> Back to Onboarding
        </button>
      </div>
    </div>

    <div class="content-section">
      <div class="user-form-container">
        <form class="onboarding-form" @submit.prevent="submitCreate">
          <div class="form-grid">
            <!-- Company -->
            <div class="form-group">
              <label for="company">Company *</label>
              <input type="text" id="company" v-model="user.company" required
                     placeholder="e.g., Americor">
            </div>
            
            <!-- Legal Name -->
            <div class="form-group">
              <label for="legalName">Legal Name *</label>
              <input type="text" id="legalName" v-model="user.legalName" required>
            </div>
            
            <!-- Display Name -->
            <div class="form-group">
              <label for="displayName">Display Name *</label>
              <input type="text" id="displayName" v-model="user.displayName" required>
            </div>
            
            <!-- Display Last Name -->
            <div class="form-group">
              <label for="displayLastName">Display Last Name *</label>
              <input type="text" id="displayLastName" v-model="user.displayLastName" required>
            </div>
            
            <!-- Personal Email -->
            <div class="form-group">
              <label for="personalEmail">Personal Email *</label>
              <input type="email" id="personalEmail" v-model="user.personalEmail" required>
            </div>
            
            <!-- Company Email -->
            <div class="form-group">
              <label for="companyEmail">Company Email</label>
              <input type="email" id="companyEmail" v-model="user.companyEmail" 
                     placeholder="Auto-generated as username@americor.com" readonly class="readonly-field">
            </div>
            
            <!-- Phone Number -->
            <div class="form-group">
              <label for="phoneNumber">Phone Number</label>
              <input type="tel" id="phoneNumber" v-model="user.phoneNumber" 
                     placeholder="949-555-8515">
            </div>
            
            <!-- Title -->
            <div class="form-group">
              <label for="title">Title *</label>
              <input type="text" id="title" v-model="user.title" required>
            </div>
            
            <!-- Manager -->
            <div class="form-group">
              <label for="managerEmail">Manager's Email *</label>
              <input type="email" id="managerEmail" v-model="user.managerEmail" required>
            </div>
            
            <!-- Department -->
            <div class="form-group">
              <label for="department">Department *</label>
              <select id="department" v-model="user.department" required>
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
              <label for="startDate">Start Date *</label>
              <input type="date" id="startDate" v-model="user.startDate" required>
            </div>
            
            <!-- Location First Day -->
            <div class="form-group">
              <label for="locationFirstDay">Location First Day</label>
              <input type="text" id="locationFirstDay" v-model="user.locationFirstDay" 
                     placeholder="e.g., Remote">
            </div>
            
            <!-- Username -->
            <div class="form-group">
              <label for="username">Username</label>
              <input type="text" id="username" v-model="user.username" 
                     placeholder="Auto-generated as firstname.lastname" readonly class="readonly-field">
            </div>
            
            <!-- Password -->
            <div class="form-group">
              <label for="password">Password</label>
              <div class="password-field-container">
                <input type="text" id="password" v-model="user.password" 
                       placeholder="Auto-generated 16-character password" readonly class="readonly-field">
                <button type="button" class="btn-outline btn-small" @click="renewPassword">
                  <i class="fa-solid fa-refresh"></i> 
                </button>
              </div>
            </div>
            
            <!-- Department OU -->
            <div class="form-group">
              <label for="departmentOU">Department OU</label>
              <input 
                type="text" 
                id="departmentOU" 
                v-model="user.departmentOU"
                readonly
                :placeholder="user.department ? getDepartmentOU(user.department) || 'OU will be assigned automatically' : 'Select department first'"
                class="readonly-field"
              >
            </div>
            
            <!-- Credit9 Alias -->
            <div class="form-group">
              <label for="credit9Alias">credit9.com Alias</label>
              <input type="text" id="credit9Alias" v-model="user.credit9Alias" 
                     placeholder="Auto-generated as username@credit9.com" readonly class="readonly-field">
            </div>
            
            <!-- Advantageteam Alias -->
            <div class="form-group">
              <label for="advantageAlias">advantageteam.law Alias</label>
              <input type="text" id="advantageAlias" v-model="user.advantageAlias" 
                     placeholder="Auto-generated as username@advantageteam.law" readonly class="readonly-field">
            </div>
            
            <!-- Address Type -->
            <div class="form-group">
              <label for="addressType">Address Type</label>
              <select id="addressType" v-model="user.addressType">
                <option value="Residential">Residential</option>
                <option value="Commercial">Commercial</option>
                <option value="PO Box">PO Box</option>
              </select>
            </div>
            
            <!-- Street Name -->
            <div class="form-group">
              <label for="streetName">Street Name</label>
              <input type="text" id="streetName" v-model="user.streetName" 
                     placeholder="123 Main St">
            </div>
            
            <!-- City -->
            <div class="form-group">
              <label for="city">City</label>
              <input type="text" id="city" v-model="user.city" 
                     placeholder="City">
            </div>
            
            <!-- State -->
            <div class="form-group">
              <label for="state">State</label>
              <input type="text" id="state" v-model="user.state" 
                     placeholder="CA" maxlength="2">
            </div>
            
            <!-- Zip Code -->
            <div class="form-group">
              <label for="zipCode">Zip Code</label>
              <input type="text" id="zipCode" v-model="user.zipCode" 
                     placeholder="12345" maxlength="10">
            </div>
            
            <!-- Hostname -->
            <div class="form-group">
              <label for="hostname">System Hostname</label>
              <input type="text" id="hostname" v-model="user.hostname" 
                     placeholder="A-XXXXXXXX">
            </div>
            
            <!-- Ticket Number -->
            <div class="form-group">
              <label for="ticketNumber">Ticket # *</label>
              <input type="text" id="ticketNumber" v-model="user.ticketNumber" required
                     placeholder="e.g., TKT-2025-001">
            </div>
            
            <!-- Zoom & Five9 Combined -->
            <div class="form-group">
              <label>Access Type</label>
              <div class="checkbox-group">
                <label class="checkbox-label">
                  <input type="checkbox" id="zoom" v-model="user.zoom" @change="handleZoomChange">
                  <span class="checkmark"></span>
                  Zoom
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" id="five9" v-model="user.five9" @change="handleFive9Change">
                  <span class="checkmark"></span>
                  Five9
                </label>
              </div>
            </div>
            
            <!-- Extension -->
            <div class="form-group">
              <label for="extension">Extension</label>
              <input type="number" id="extension" v-model="user.extension" 
                     placeholder="e.g., 1234">
            </div>
            
            <!-- Notes -->
            <div class="form-group">
              <label for="notes">Notes</label>
              <textarea id="notes" v-model="user.notes" 
                        placeholder="Internal notes..."
                        rows="3"></textarea>
            </div>
            
            <!-- Extra Details -->
            <div class="form-group">
              <label for="extraDetails">Extra Details</label>
              <textarea id="extraDetails" v-model="user.extraDetails" 
                        placeholder="Additional notes or special requirements..."
                        rows="3"></textarea>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="resetForm">Reset Form</button>
            <button type="button" class="btn-secondary" @click="goBack">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="creating">
              <i class="fa-solid fa-plus"></i> 
              {{ creating ? 'Creating...' : 'Create User' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { useDepartmentMappings } from '@/composables/useDepartmentMappings'
import axios from 'axios'

export default {
  name: 'CreateUser',
  setup() {
    const { sortedDepartments, getDepartmentOU } = useDepartmentMappings()
    
    return {
      sortedDepartments,
      getDepartmentOU
    }
  },
  data() {
    return {
      user: this.createEmptyUser(),
      creating: false
    }
  },
  watch: {
    user: {
      handler(newUser) {
        if (!newUser) return
        
        // Auto-generate username when display name/last name changes
        if (newUser.displayName && newUser.displayLastName) {
          newUser.username = `${newUser.displayName.toLowerCase()}.${newUser.displayLastName.toLowerCase()}`
          
          // Auto-generate company email using the username
          newUser.companyEmail = `${newUser.username}@americor.com`
          
          // Auto-populate alias fields using the username
          newUser.advantageAlias = `${newUser.username}@advantageteam.law`
          newUser.credit9Alias = `${newUser.username}@credit9.com`
        } else {
          // Clear fields when names are not complete
          newUser.username = ''
          newUser.companyEmail = ''
          newUser.advantageAlias = ''
          newUser.credit9Alias = ''
        }
        
        // Auto-populate Department OU when department changes
        if (newUser.department) {
          newUser.departmentOU = this.getDepartmentOU(newUser.department)
        } else {
          newUser.departmentOU = ''
        }
      },
      deep: true
    }
  },
  methods: {
    createEmptyUser() {
      const user = {
        company: 'Americor',
        legalName: '',
        displayName: '',
        displayLastName: '',
        personalEmail: '',
        companyEmail: '',
        phoneNumber: '',
        title: '',
        managerEmail: '',
        department: '',
        startDate: new Date().toISOString().split('T')[0], // Default to today
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
        ticketNumber: '',
        extension: null,
        zoom: false,
        five9: false,
        notes: '',
        extraDetails: ''
      }
      // Auto-generate password immediately
      user.password = this.generatePassword()
      return user
    },
    
    async submitCreate() {
      this.creating = true
      
      try {
        // Auto-generate missing fields
        if (!this.user.username && this.user.displayName && this.user.displayLastName) {
          this.user.username = `${this.user.displayName.toLowerCase()}.${this.user.displayLastName.toLowerCase()}`
        }
        if (!this.user.companyEmail && this.user.username) {
          this.user.companyEmail = `${this.user.username}@americor.com`
        }
        if (!this.user.advantageAlias && this.user.username) {
          this.user.advantageAlias = `${this.user.username}@advantageteam.law`
        }
        if (!this.user.credit9Alias && this.user.username) {
          this.user.credit9Alias = `${this.user.username}@credit9.com`
        }
        if (!this.user.departmentOU && this.user.department) {
          this.user.departmentOU = this.getDepartmentOU(this.user.department)
        }
        if (!this.user.password) {
          this.user.password = this.generatePassword()
        }
        
        // Set default values for missing fields
        const defaultValues = {
          company: 'Americor',
          phoneNumber: '555-0000',
          addressType: 'Residential',
          streetName: '123 Main St',
          city: 'City',
          state: 'CA',
          zipCode: '12345'
        }
        
        Object.keys(defaultValues).forEach(key => {
          if (!this.user[key] || this.user[key].trim() === '') {
            this.user[key] = defaultValues[key]
          }
        })
        
        // Get current user email for created_by tracking
        const currentUserEmail = this.getCurrentUserEmail()
        
        // Validate required fields before submission
        const requiredFields = [
          { field: 'legalName', label: 'Legal Name' },
          { field: 'displayName', label: 'Display Name' },
          { field: 'displayLastName', label: 'Display Last Name' },
          { field: 'personalEmail', label: 'Personal Email' },
          { field: 'title', label: 'Title' },
          { field: 'managerEmail', label: 'Manager Email' },
          { field: 'department', label: 'Department' },
          { field: 'startDate', label: 'Start Date' }
        ]
        
        const missingFields = requiredFields.filter(req => !this.user[req.field] || this.user[req.field].trim() === '')
        if (missingFields.length > 0) {
          alert(`Please fill in the following required fields:\n${missingFields.map(f => f.label).join('\n')}`)
          return
        }
        
        // Validate email formats
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(this.user.personalEmail)) {
          alert('Please enter a valid personal email address')
          return
        }
        if (this.user.managerEmail && !emailRegex.test(this.user.managerEmail)) {
          alert('Please enter a valid manager email address')
          return
        }
        
        const onboardingData = {
          company: this.user.company,
          legal_name: this.user.legalName,
          display_name: this.user.displayName,
          display_last_name: this.user.displayLastName,
          personal_email: this.user.personalEmail,
          company_email: this.user.companyEmail,
          phone_number: this.user.phoneNumber ? String(this.user.phoneNumber) : null,
          title: this.user.title,
          manager: this.user.managerEmail,
          department: this.user.department,
          start_date: this.user.startDate ? new Date(this.user.startDate).toISOString() : new Date().toISOString(),
          location_first_day: this.user.locationFirstDay || null,
          username: this.user.username,
          password: this.user.password,
          department_ou: this.user.departmentOU,
          credit9_alias: this.user.credit9Alias,
          advantageteam_alias: this.user.advantageAlias,
          address_type: this.user.addressType,
          street_name: this.user.streetName,
          city: this.user.city,
          state: this.user.state,
          zip_code: this.user.zipCode ? String(this.user.zipCode) : null,
          hostname: this.user.hostname,
          ticket_number: this.user.ticketNumber ? String(this.user.ticketNumber) : null,
          extension: this.user.extension ? String(this.user.extension) : null,
          zoom: this.user.zoom,
          five9: this.user.five9,
          notes: this.user.notes || null,
          extra_details: this.user.extraDetails || null
        }
        
        console.log('Creating new user:', onboardingData)
        console.log('User email:', currentUserEmail)
        console.log('Full request URL:', `/api/v1/onboarding/?user_email=${encodeURIComponent(currentUserEmail)}`)
        await axios.post(`/api/v1/onboarding/?user_email=${encodeURIComponent(currentUserEmail)}`, onboardingData)
        
        alert('User created successfully!')
        this.goBack()
      } catch (error) {
        console.error('Error creating user:', error)
        console.error('Error response:', error.response)
        console.error('Error response data:', error.response?.data)
        
        // Better error handling to show actual validation errors
        if (error.response?.data?.detail) {
          if (Array.isArray(error.response.data.detail)) {
            const errors = error.response.data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join('\n')
            alert('Validation errors:\n' + errors)
          } else {
            alert('Error: ' + error.response.data.detail)
          }
        } else {
          alert('Error creating user: ' + error.message)
        }
      } finally {
        this.creating = false
      }
    },
    
    generatePassword() {
      const chars = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$+!&='
      let password = ''
      for (let i = 0; i < 16; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length))
      }
      return password
    },

    renewPassword() {
      this.user.password = this.generatePassword()
    },
    
    handleZoomChange() {
      if (this.user.zoom && this.user.five9) {
        this.user.five9 = false
      }
    },
    
    handleFive9Change() {
      if (this.user.five9 && this.user.zoom) {
        this.user.zoom = false
      }
    },
    
    resetForm() {
      this.user = this.createEmptyUser()
    },
    
    goBack() {
      this.$router.push({ name: 'onboarding' })
    },

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
    }
  }
}
</script>

<style scoped>
.create-user-page {
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

.user-form-container {
  padding: 24px;
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

.password-field-container {
  display: flex;
  gap: 8px;
  align-items: center;
}

.password-field-container input {
  flex: 1;
}

.btn-small {
  padding: 6px 10px;
  font-size: 0.8rem;
  white-space: nowrap;
}

/* Checkbox styles */
.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.85rem;
  color: #374151;
  margin-bottom: 0;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 8px;
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"]:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.checkbox-group {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.checkbox-group .checkbox-label {
  margin-bottom: 4px;
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
}

.btn-primary:hover:not(:disabled) {
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

  .form-actions {
    flex-direction: column;
  }
}
</style>
