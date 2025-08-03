<template>
  <div class="offboarded-users-page">
    <div class="page-header">
      <h1>Offboarded Users Information</h1>
      <p>Review information about previously offboarded users</p>
    </div>

    <div class="content-section">
      <div class="section-header">
        <h2>Offboarded Users</h2>
        <div class="header-actions">
          <div class="search-box">
            <input 
              type="text" 
              placeholder="Search users..." 
              v-model="searchQuery"
              @input="filterUsers"
            >
            <button class="search-btn">🔍</button>
          </div>
          <button class="btn-secondary" @click="exportData">📊 Export</button>
        </div>
      </div>
      
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Department</th>
              <th>Position</th>
              <th>Last Working Day</th>
              <th>Reason</th>
              <th>Offboarded By</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td>
                <div class="user-name">{{ user.firstName }} {{ user.lastName }}</div>
              </td>
              <td>{{ user.email }}</td>
              <td>{{ user.department }}</td>
              <td>{{ user.position }}</td>
              <td>{{ formatDate(user.lastWorkingDay) }}</td>
              <td>
                <span class="reason-badge" :class="user.reason">{{ formatReason(user.reason) }}</span>
              </td>
              <td>{{ user.offboardedBy }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-sm btn-info" @click="viewDetails(user)">👁️ View</button>
                  <button class="btn-sm btn-primary" @click="downloadInfo(user)">📄 Download</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- User Details Modal -->
    <div v-if="selectedUser" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedUser.firstName }} {{ selectedUser.lastName }} - Offboarding Details</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="details-grid">
            <div class="detail-section">
              <h4>Personal Information</h4>
              <div class="detail-item">
                <span class="label">Name:</span>
                <span class="value">{{ selectedUser.firstName }} {{ selectedUser.lastName }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Email:</span>
                <span class="value">{{ selectedUser.email }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Employee ID:</span>
                <span class="value">{{ selectedUser.employeeId }}</span>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>Work Information</h4>
              <div class="detail-item">
                <span class="label">Department:</span>
                <span class="value">{{ selectedUser.department }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Position:</span>
                <span class="value">{{ selectedUser.position }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Manager:</span>
                <span class="value">{{ selectedUser.manager }}</span>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>Offboarding Information</h4>
              <div class="detail-item">
                <span class="label">Last Working Day:</span>
                <span class="value">{{ formatDate(selectedUser.lastWorkingDay) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Reason:</span>
                <span class="value">{{ formatReason(selectedUser.reason) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Offboarded By:</span>
                <span class="value">{{ selectedUser.offboardedBy }}</span>
              </div>
            </div>
            
            <div class="detail-section full-width">
              <h4>Notes</h4>
              <p class="notes">{{ selectedUser.notes || 'No additional notes' }}</p>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModal">Close</button>
          <button class="btn-primary" @click="downloadInfo(selectedUser)">📄 Download Info</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OffboardedUsersView',
  data() {
    return {
      searchQuery: '',
      selectedUser: null,
      users: [
        {
          id: 1,
          firstName: 'Sarah',
          lastName: 'Johnson',
          email: 'sarah.johnson@company.com',
          department: 'Finance',
          position: 'Financial Analyst',
          employeeId: 'EMP005',
          lastWorkingDay: new Date('2025-07-15'),
          reason: 'resignation',
          offboardedBy: 'Mike Wilson',
          manager: 'Tom Anderson',
          notes: 'Left for better opportunity. Good employee, eligible for rehire.'
        },
        {
          id: 2,
          firstName: 'David',
          lastName: 'Brown',
          email: 'david.brown@company.com',
          department: 'IT',
          position: 'System Administrator',
          employeeId: 'EMP006',
          lastWorkingDay: new Date('2025-06-30'),
          reason: 'termination',
          offboardedBy: 'Lisa Garcia',
          manager: 'Sarah Davis',
          notes: 'Performance issues. Not eligible for rehire.'
        },
        {
          id: 3,
          firstName: 'Carol',
          lastName: 'Smith',
          email: 'carol.smith@company.com',
          department: 'HR',
          position: 'HR Manager',
          employeeId: 'EMP007',
          lastWorkingDay: new Date('2025-06-15'),
          reason: 'retirement',
          offboardedBy: 'John Smith',
          manager: 'CEO',
          notes: 'Retired after 25 years of service. Excellent employee.'
        },
        {
          id: 4,
          firstName: 'Alex',
          lastName: 'Wilson',
          email: 'alex.wilson@company.com',
          department: 'Marketing',
          position: 'Marketing Coordinator',
          employeeId: 'EMP008',
          lastWorkingDay: new Date('2025-05-31'),
          reason: 'contract-end',
          offboardedBy: 'Mike Wilson',
          manager: 'Tom Anderson',
          notes: 'Contract completed successfully. Available for future projects.'
        }
      ],
      filteredUsers: []
    }
  },
  mounted() {
    this.filteredUsers = this.users
  },
  methods: {
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
        user.department.toLowerCase().includes(query)
      )
    },
    viewDetails(user) {
      this.selectedUser = user
    },
    closeModal() {
      this.selectedUser = null
    },
    downloadInfo(user) {
      // Generate downloadable info
      const info = `
Offboarded User Information
==========================

Personal Information:
- Name: ${user.firstName} ${user.lastName}
- Email: ${user.email}
- Employee ID: ${user.employeeId}

Work Information:
- Department: ${user.department}
- Position: ${user.position}
- Manager: ${user.manager}

Offboarding Information:
- Last Working Day: ${this.formatDate(user.lastWorkingDay)}
- Reason: ${this.formatReason(user.reason)}
- Offboarded By: ${user.offboardedBy}

Notes:
${user.notes || 'No additional notes'}
      `.trim()
      
      const blob = new Blob([info], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${user.firstName}_${user.lastName}_offboarding_info.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    },
    exportData() {
      const csvContent = [
        ['Name', 'Email', 'Department', 'Position', 'Last Working Day', 'Reason', 'Offboarded By'],
        ...this.filteredUsers.map(user => [
          `${user.firstName} ${user.lastName}`,
          user.email,
          user.department,
          user.position,
          this.formatDate(user.lastWorkingDay),
          this.formatReason(user.reason),
          user.offboardedBy
        ])
      ].map(row => row.join(',')).join('\n')
      
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'offboarded_users.csv'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    },
    formatDate(date) {
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(date)
    },
    formatReason(reason) {
      const reasons = {
        resignation: 'Resignation',
        termination: 'Termination',
        retirement: 'Retirement',
        'contract-end': 'Contract End',
        other: 'Other'
      }
      return reasons[reason] || reason
    }
  }
}
</script>

<style scoped>
.offboarded-users-page {
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

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 8px 12px;
}

.search-box input {
  border: none;
  background: none;
  outline: none;
  padding: 4px 8px;
  width: 200px;
}

.search-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  text-align: left;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.users-table th {
  background: #f9fafb;
  color: #6b7280;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.users-table tbody tr:hover {
  background: #f9fafb;
}

.user-name {
  font-weight: 600;
  color: #1f2937;
}

.reason-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.reason-badge.resignation {
  background: #eff6ff;
  color: #2563eb;
}

.reason-badge.termination {
  background: #fef2f2;
  color: #dc2626;
}

.reason-badge.retirement {
  background: #f0fdf4;
  color: #16a34a;
}

.reason-badge.contract-end {
  background: #fef3c7;
  color: #d97706;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-info {
  background: #eff6ff;
  color: #2563eb;
}

.btn-info:hover {
  background: #dbeafe;
}

.btn-primary {
  background: #667eea;
  color: white;
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
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #e5e7eb;
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
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.2rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 4px;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  padding: 30px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.detail-section {
  background: #f8fafc;
  border-radius: 8px;
  padding: 20px;
}

.detail-section.full-width {
  grid-column: 1 / -1;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 500;
  color: #374151;
  min-width: 100px;
}

.value {
  color: #1f2937;
  text-align: right;
}

.notes {
  margin: 0;
  color: #6b7280;
  line-height: 1.5;
  font-style: italic;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
</style>
