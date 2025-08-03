import { ref, computed } from 'vue'

// Global shared state for department mappings
const departmentMappings = ref([
  { department: 'ACCOUNTING', ou: '/Accounting', isEditing: false, originalData: null },
  { department: 'AFFILIATE PARTNERSHIPS', ou: '/Affiliate Partnerships', isEditing: false, originalData: null },
  { department: 'CLIENT SERVICES', ou: '/Client Services', isEditing: false, originalData: null },
  { department: 'COMPLIANCE', ou: '/Compliance', isEditing: false, originalData: null },
  { department: 'CONTRACTORS ASCENDUM', ou: '/External Contractors/Ascendum', isEditing: false, originalData: null },
  { department: 'CONTRACTORS BPOGS', ou: '/External Contractors/BPOGS', isEditing: false, originalData: null },
  { department: 'CONTRACTORS BUWELO', ou: '/External Contractors/Buwelo', isEditing: false, originalData: null },
  { department: 'CONTRACTORS FUSION', ou: '/External Contractors/Fusion', isEditing: false, originalData: null },
  { department: 'CONTRACTORS VXI', ou: '/External Contractors/VXI', isEditing: false, originalData: null },
  { department: 'CONTRACTORS KIPI', ou: '/External Contractors/Kipi', isEditing: false, originalData: null },
  { department: 'DATA ANALYTICS', ou: '/Process Analytics', isEditing: false, originalData: null },
  { department: 'EXECUTIVES', ou: '/Executive Administration', isEditing: false, originalData: null },
  { department: 'HUMAN RESOURCES', ou: '/Human Resources', isEditing: false, originalData: null },
  { department: 'IT DEVELOPMENT', ou: '/IT/IT Development', isEditing: false, originalData: null },
  { department: 'IT SUPPORT', ou: '/IT/IT Operations', isEditing: false, originalData: null },
  { department: 'LEARNING & DEVELOPMENT', ou: '/Learning and Development', isEditing: false, originalData: null },
  { department: 'LEGAL', ou: '/Legal', isEditing: false, originalData: null },
  { department: 'LOAN CONSULTANTS', ou: '/Loans (Credit 9)', isEditing: false, originalData: null },
  { department: 'LOAN UNDERWRITING', ou: '/Loans (Credit 9)', isEditing: false, originalData: null },
  { department: 'LOAN PROCESSING', ou: '/Loans (Credit 9)', isEditing: false, originalData: null },
  { department: 'LOANS', ou: '/Loans (Credit 9)', isEditing: false, originalData: null },
  { department: 'MARKETING', ou: '/Marketing', isEditing: false, originalData: null },
  { department: 'NEGOTIATIONS', ou: '/Negotiations', isEditing: false, originalData: null },
  { department: 'PAYMENTS', ou: '/Payments & Enrollments', isEditing: false, originalData: null },
  { department: 'PROCESS ANALYTICS', ou: '/Process Analytics', isEditing: false, originalData: null },
  { department: 'SALES', ou: '/Client Advocates', isEditing: false, originalData: null },
  { department: 'AZ-CLIENT SERVICES', ou: '/Scottsdale Office/Client Services', isEditing: false, originalData: null },
  { department: 'AZ-SALES', ou: '/Scottsdale Office/Sales', isEditing: false, originalData: null },
  { department: 'ML', ou: '/Mission Loans', isEditing: false, originalData: null },
  { department: 'ML-SALES', ou: '/Mission Loans', isEditing: false, originalData: null },
  { department: 'ADVANTAGE LAW', ou: '/External Contractors/Legal Partners', isEditing: false, originalData: null }
])

export function useDepartmentMappings() {
  // Computed property for sorted department list
  const sortedDepartments = computed(() => {
    return [...departmentMappings.value].sort((a, b) => 
      a.department.localeCompare(b.department)
    )
  })

  // Get OU for a specific department
  const getDepartmentOU = (departmentName) => {
    const mapping = departmentMappings.value.find(
      m => m.department.toUpperCase() === departmentName.toUpperCase()
    )
    return mapping ? mapping.ou : ''
  }

  // Update mappings (for Settings component)
  const updateMappings = (newMappings) => {
    departmentMappings.value = newMappings
  }

  // Add a new mapping
  const addMapping = (department, ou) => {
    departmentMappings.value.push({ department, ou })
  }

  // Remove a mapping
  const removeMapping = (index) => {
    departmentMappings.value.splice(index, 1)
  }

  // Reset to defaults
  const resetToDefaults = () => {
    departmentMappings.value = [
      { department: 'ACCOUNTING', ou: '/Accounting', isEditing: false, originalData: null },
      { department: 'AFFILIATE PARTNERSHIPS', ou: '/Affiliate Partnerships', isEditing: false, originalData: null },
      { department: 'CLIENT SERVICES', ou: '/Client Services', isEditing: false, originalData: null },
      { department: 'COMPLIANCE', ou: '/Compliance', isEditing: false, originalData: null },
      { department: 'CONTRACTORS ASCENDUM', ou: '/External Contractors/Ascendum', isEditing: false, originalData: null },
      { department: 'CONTRACTORS BPOGS', ou: '/External Contractors/BPOGS', isEditing: false, originalData: null },
      { department: 'CONTRACTORS BUWELO', ou: '/External Contractors/Buwelo', isEditing: false, originalData: null },
      { department: 'CONTRACTORS FUSION', ou: '/External Contractors/Fusion', isEditing: false, originalData: null },
      { department: 'CONTRACTORS VXI', ou: '/External Contractors/VXI', isEditing: false, originalData: null },
      { department: 'CONTRACTORS KIPI', ou: '/External Contractors/Kipi', isEditing: false, originalData: null },
      { department: 'DATA ANALYTICS', ou: '/Process Analytics', isEditing: false, originalData: null },
      { department: 'EXECUTIVES', ou: '/Executive Administration', isEditing: false, originalData: null },
      { department: 'HUMAN RESOURCES', ou: '/Human Resources', isEditing: false, originalData: null },
      { department: 'IT DEVELOPMENT', ou: '/IT/IT Development', isEditing: false, originalData: null },
      { department: 'IT SUPPORT', ou: '/IT/IT Operations', isEditing: false, originalData: null },
      { department: 'LEARNING & DEVELOPMENT', ou: '/Learning and Development', isEditing: false, originalData: null },
      { department: 'LEGAL', ou: '/Legal', isEditing: false, originalData: null },
      { department: 'LOAN CONSULTANTS', ou: '/Loans (Credit 9)', isEditing: false, originalData: null },
      { department: 'LOAN UNDERWRITING', ou: '/Loans (Credit 9)', isEditing: false, originalData: null },
      { department: 'LOAN PROCESSING', ou: '/Loans (Credit 9)', isEditing: false, originalData: null },
      { department: 'LOANS', ou: '/Loans (Credit 9)', isEditing: false, originalData: null },
      { department: 'MARKETING', ou: '/Marketing', isEditing: false, originalData: null },
      { department: 'NEGOTIATIONS', ou: '/Negotiations', isEditing: false, originalData: null },
      { department: 'PAYMENTS', ou: '/Payments & Enrollments', isEditing: false, originalData: null },
      { department: 'PROCESS ANALYTICS', ou: '/Process Analytics', isEditing: false, originalData: null },
      { department: 'SALES', ou: '/Client Advocates', isEditing: false, originalData: null },
      { department: 'AZ-CLIENT SERVICES', ou: '/Scottsdale Office/Client Services', isEditing: false, originalData: null },
      { department: 'AZ-SALES', ou: '/Scottsdale Office/Sales', isEditing: false, originalData: null },
      { department: 'ML', ou: '/Mission Loans', isEditing: false, originalData: null },
      { department: 'ML-SALES', ou: '/Mission Loans', isEditing: false, originalData: null },
      { department: 'ADVANTAGE LAW', ou: '/External Contractors/Legal Partners', isEditing: false, originalData: null }
    ]
  }

  return {
    departmentMappings,
    sortedDepartments,
    getDepartmentOU,
    updateMappings,
    addMapping,
    removeMapping,
    resetToDefaults
  }
}
