// Authentication and authorization composable
import { ref, computed } from 'vue'

// User roles
const USER_ROLES = {
  ADMIN: 'admin',
  IT: 'it', 
  USER: 'user'
}

// User permissions
const USER_PERMISSIONS = {
  CREATE_USER: 'create_user',
  EDIT_USER: 'edit_user',
  DELETE_USER: 'delete_user',
  VIEW_USER: 'view_user',
  BULK_ONBOARD: 'bulk_onboard',
  BULK_OFFBOARD: 'bulk_offboard',
  EXECUTE_SCRIPTS: 'execute_scripts',
  VIEW_SCRIPT_LOGS: 'view_script_logs',
  MANAGE_SETTINGS: 'manage_settings',
  VIEW_AUDIT_LOGS: 'view_audit_logs'
}

// Role to permissions mapping (matches backend auth.py)
const ROLE_PERMISSIONS = {
  [USER_ROLES.ADMIN]: [
    USER_PERMISSIONS.CREATE_USER,
    USER_PERMISSIONS.EDIT_USER,
    USER_PERMISSIONS.DELETE_USER,
    USER_PERMISSIONS.VIEW_USER,
    USER_PERMISSIONS.BULK_ONBOARD,
    USER_PERMISSIONS.BULK_OFFBOARD,
    USER_PERMISSIONS.EXECUTE_SCRIPTS,
    USER_PERMISSIONS.VIEW_SCRIPT_LOGS,
    USER_PERMISSIONS.MANAGE_SETTINGS,
    USER_PERMISSIONS.VIEW_AUDIT_LOGS
  ],
  [USER_ROLES.IT]: [
    USER_PERMISSIONS.CREATE_USER,
    USER_PERMISSIONS.EDIT_USER,
    USER_PERMISSIONS.VIEW_USER,
    USER_PERMISSIONS.BULK_ONBOARD,
    USER_PERMISSIONS.BULK_OFFBOARD,
    USER_PERMISSIONS.EXECUTE_SCRIPTS,
    USER_PERMISSIONS.VIEW_SCRIPT_LOGS,
    USER_PERMISSIONS.MANAGE_SETTINGS
  ],
  [USER_ROLES.USER]: [
    USER_PERMISSIONS.VIEW_USER
  ]
}

// Admin users (fallback)
const ADMIN_USERS = [
  'cristian.rodriguez@americor.com'
]

export function useAuth() {
  const currentUser = ref(null)
  const userRole = ref(null)
  const userPermissions = ref([])

  // Determine user role based on email and JumpCloud groups/attributes
  const determineRole = (email, groups = []) => {
    // Check if user is in admin list (fallback)
    if (ADMIN_USERS.includes(email)) {
      return USER_ROLES.ADMIN
    }

    // Check JumpCloud Role attribute and groups
    for (const groupOrRole of groups) {
      const groupLower = groupOrRole.toLowerCase()
      
      // Check for exact role matches from SAML Role attribute
      if (groupLower === 'help desk management tool - admin' || groupLower === 'admin') {
        return USER_ROLES.ADMIN
      } else if (groupLower === 'help desk management tool - it' || groupLower === 'it') {
        return USER_ROLES.IT
      }
      
      // Check for partial matches (legacy support)
      else if (groupLower.includes('admin')) {
        return USER_ROLES.ADMIN
      } else if (groupLower.includes('it') || groupLower.includes('information technology')) {
        return USER_ROLES.IT
      }
    }

    // Default to USER role
    return USER_ROLES.USER
  }

  // Parse user from SSO claims
  const parseUserFromSSO = (claims) => {
    // Get email from claims
    let email = claims.email || claims.preferred_username
    if (!email) {
      throw new Error('No email found in SSO claims')
    }

    // If email is just username, construct full email
    if (typeof email === 'string' && !email.includes('@')) {
      email = `${email}@americor.com`
    }

    // Handle array values
    if (Array.isArray(email)) {
      email = email[0]
    }

    // Get name from claims
    let name = claims.name
    if (!name) {
      const givenName = claims.given_name || ''
      const familyName = claims.family_name || ''
      name = `${givenName} ${familyName}`.trim() || email.split('@')[0]
    }

    // Handle array values
    if (Array.isArray(name)) {
      name = name[0]
    }

    // Get groups/roles from JumpCloud claims
    let groups = claims.groups || []
    if (typeof groups === 'string') {
      groups = [groups]
    }

    // Get Role attribute from SAML (this is what you're using)
    const roleAttribute = claims.Role || claims.role
    if (roleAttribute) {
      if (Array.isArray(roleAttribute)) {
        groups.push(...roleAttribute)
      } else {
        groups.push(roleAttribute)
      }
    }

    console.log('SSO Claims - Email:', email, 'Name:', name, 'Groups/Roles:', groups)

    const role = determineRole(email, groups)
    const permissions = ROLE_PERMISSIONS[role] || []

    return {
      email,
      name,
      groups,
      role,
      permissions
    }
  }

  // Initialize user from session storage
  const initializeUser = () => {
    try {
      const userClaims = sessionStorage.getItem('userClaims')
      if (userClaims) {
        const claims = JSON.parse(userClaims)
        const user = parseUserFromSSO(claims)
        
        currentUser.value = user
        userRole.value = user.role
        userPermissions.value = user.permissions
        
        console.log('User initialized:', user)
        return user
      }
    } catch (error) {
      console.error('Error initializing user from SSO claims:', error)
    }
    
    // Development fallback
    if (process.env.NODE_ENV === 'development') {
      console.warn('Development mode: using cristian.rodriguez@americor.com as admin')
      const devUser = {
        email: 'cristian.rodriguez@americor.com',
        name: 'Cristian Rodriguez',
        groups: ['admin'],
        role: USER_ROLES.ADMIN,
        permissions: ROLE_PERMISSIONS[USER_ROLES.ADMIN]
      }
      
      currentUser.value = devUser
      userRole.value = devUser.role
      userPermissions.value = devUser.permissions
      
      return devUser
    }
    
    return null
  }

  // Get current user email for API calls
  const getCurrentUserEmail = () => {
    if (currentUser.value?.email) {
      return currentUser.value.email
    }
    
    // Try to get from session storage directly
    try {
      const userClaims = sessionStorage.getItem('userClaims')
      if (userClaims) {
        const claims = JSON.parse(userClaims)
        const user = parseUserFromSSO(claims)
        return user.email
      }
    } catch (error) {
      console.error('Error getting user email:', error)
    }
    
    // Development fallback
    if (process.env.NODE_ENV === 'development') {
      return 'cristian.rodriguez@americor.com'
    }
    
    throw new Error('User not authenticated via SSO')
  }

  // Get SSO claims for API calls
  const getSSOClaims = () => {
    const userClaims = sessionStorage.getItem('userClaims')
    return userClaims || null
  }

  // Permission checking
  const hasPermission = (permission) => {
    if (!currentUser.value) {
      initializeUser()
    }
    return userPermissions.value.includes(permission)
  }

  const isAdmin = () => {
    if (!currentUser.value) {
      initializeUser()
    }
    return userRole.value === USER_ROLES.ADMIN
  }

  const isIT = () => {
    if (!currentUser.value) {
      initializeUser()
    }
    return userRole.value === USER_ROLES.IT
  }

  // Computed permission flags
  const canCreateUser = computed(() => hasPermission(USER_PERMISSIONS.CREATE_USER))
  const canEditUser = computed(() => hasPermission(USER_PERMISSIONS.EDIT_USER))
  const canDeleteUser = computed(() => hasPermission(USER_PERMISSIONS.DELETE_USER))
  const canViewUser = computed(() => hasPermission(USER_PERMISSIONS.VIEW_USER))
  const canBulkOnboard = computed(() => hasPermission(USER_PERMISSIONS.BULK_ONBOARD))
  const canBulkOffboard = computed(() => hasPermission(USER_PERMISSIONS.BULK_OFFBOARD))
  const canExecuteScripts = computed(() => hasPermission(USER_PERMISSIONS.EXECUTE_SCRIPTS))
  const canViewScriptLogs = computed(() => hasPermission(USER_PERMISSIONS.VIEW_SCRIPT_LOGS))
  const canManageSettings = computed(() => hasPermission(USER_PERMISSIONS.MANAGE_SETTINGS))
  const canViewAuditLogs = computed(() => hasPermission(USER_PERMISSIONS.VIEW_AUDIT_LOGS))

  // Initialize on first use
  if (!currentUser.value) {
    initializeUser()
  }

  return {
    // State
    currentUser: computed(() => currentUser.value),
    userRole: computed(() => userRole.value),
    userPermissions: computed(() => userPermissions.value),
    
    // Methods
    initializeUser,
    getCurrentUserEmail,
    getSSOClaims,
    hasPermission,
    isAdmin,
    isIT,
    
    // Permission flags
    canCreateUser,
    canEditUser,
    canDeleteUser,
    canViewUser,
    canBulkOnboard,
    canBulkOffboard,
    canExecuteScripts,
    canViewScriptLogs,
    canManageSettings,
    canViewAuditLogs,
    
    // Constants for use in templates
    USER_ROLES,
    USER_PERMISSIONS
  }
}
