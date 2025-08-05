<template>
  <div class="create-offboarding-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>Create New Offboarding</h1>
          <p>Add a new offboarding record</p>
        </div>
        <button class="btn-secondary" @click="goBack">
          <i class="fa-solid fa-arrow-left"></i> Back to Offboarding
        </button>
      </div>
    </div>

    <div class="content-section">
      <div class="section-header">
        <h2>Offboarding Details</h2>
      </div>
      
      <div class="form-container">
        <form @submit.prevent="createRecord" class="offboarding-form">
          <div class="form-grid">
            <!-- Status -->
            <div class="form-group">
              <label for="status">Status</label>
              <select id="status" v-model="formData.status">
                <option value="Pending">Pending</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Failed">Failed</option>
              </select>
            </div>
            
            <!-- First Name -->
            <div class="form-group">
              <label for="firstName">First Name *</label>
              <input type="text" id="firstName" v-model="formData.first_name" required>
            </div>
            
            <!-- Last Name -->
            <div class="form-group">
              <label for="lastName">Last Name *</label>
              <input type="text" id="lastName" v-model="formData.last_name" required>
            </div>
            
            <!-- Company Email -->
            <div class="form-group">
              <label for="companyEmail">Company Email *</label>
              <input type="email" id="companyEmail" v-model="formData.company_email" required>
            </div>
            
            <!-- Hostname -->
            <div class="form-group">
              <label for="hostname">Hostname</label>
              <input type="text" id="hostname" v-model="formData.hostname" placeholder="e.g., LAPTOP-ABC123">
            </div>
            
            <!-- Requested By -->
            <div class="form-group">
              <label for="requestedBy">Requested By *</label>
              <input type="email" id="requestedBy" v-model="formData.requested_by" required>
            </div>
            
            <!-- Password (Auto-generated) -->
            <div class="form-group">
              <label for="password">Password (Auto-generated)</label>
              <div class="password-field">
                <input 
                  type="text" 
                  id="password" 
                  v-model="formData.password" 
                  readonly 
                  placeholder="Will be generated automatically"
                  class="readonly-field"
                >
                <button 
                  type="button" 
                  class="btn-generate" 
                  @click="generatePassword"
                  title="Generate new password"
                >
                  <i class="fa-solid fa-refresh"></i>
                </button>
              </div>
            </div>
            
            <!-- Notes -->
            <div class="form-group full-width">
              <label for="notes">Notes</label>
              <textarea id="notes" v-model="formData.notes" rows="3" placeholder="Additional notes or instructions..."></textarea>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn-outline" @click="goBack">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Creating...' : 'Create Record' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CreateOffboarding',
  data() {
    return {
      saving: false,
      formData: {
        status: 'Pending',
        first_name: '',
        last_name: '',
        company_email: '',
        hostname: '',
        requested_by: '',
        password: '',
        notes: ''
      }
    }
  },
  mounted() {
    // Generate initial password
    this.generatePassword()
  },
  methods: {
    generatePassword() {
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
      let password = ''
      for (let i = 0; i < 16; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length))
      }
      this.formData.password = password
    },
    
    async createRecord() {
      this.saving = true
      
      try {
        const currentUserEmail = this.getCurrentUserEmail()
        
        // Set created_by to current user if not provided
        const recordData = {
          ...this.formData,
          created_by: currentUserEmail
        }
        
        await axios.post(
          `/api/v1/offboarding/?user_email=${encodeURIComponent(currentUserEmail)}`,
          recordData
        )
        
        alert('Offboarding record created successfully!')
        this.goBack()
      } catch (error) {
        console.error('Error creating offboarding record:', error)
        alert('Error creating record: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.saving = false
      }
    },
    
    goBack() {
      this.$router.push('/offboarding')
    },
    
    getCurrentUserEmail() {
      // Development fallback
      if (process.env.NODE_ENV === 'development') {
        return 'cristian.rodriguez@americor.com'
      }
      
      // Try to get user data from JumpCloud SSO claims
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
        } catch (error) {
          console.error('Error parsing SSO claims:', error)
        }
      }
      
      throw new Error('User not authenticated')
    }
  }
}
</script>

<style scoped>
.create-offboarding-page {
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

.form-container {
  padding: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
  font-size: 0.9rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
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
  min-height: 80px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
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
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

.btn-primary:disabled {
  opacity: 0.5;
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

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
}

/* Password field styles */
.password-field {
  display: flex;
  gap: 8px;
  align-items: center;
}

.readonly-field {
  background-color: #f8fafc !important;
  color: #64748b;
  cursor: not-allowed;
}

.btn-generate {
  background: #667eea;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  height: 40px;
}

.btn-generate:hover {
  background: #5a67d8;
  transform: translateY(-1px);
}

.btn-generate i {
  font-size: 0.9rem;
}
</style>
