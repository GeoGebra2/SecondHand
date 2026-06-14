import { computed, reactive } from 'vue'

import http from '../api/http'

const TOKEN_KEY = 'secondhand_token'
const USER_KEY = 'secondhand_user'

function parseStoredUser() {
  const rawValue = localStorage.getItem(USER_KEY)
  if (!rawValue) {
    return null
  }

  try {
    return JSON.parse(rawValue)
  } catch {
    localStorage.removeItem(USER_KEY)
    return null
  }
}

export const authState = reactive({
  token: localStorage.getItem(TOKEN_KEY) || '',
  user: parseStoredUser(),
  initialized: false,
})

function persistAuth() {
  if (authState.token) {
    localStorage.setItem(TOKEN_KEY, authState.token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }

  if (authState.user) {
    localStorage.setItem(USER_KEY, JSON.stringify(authState.user))
  } else {
    localStorage.removeItem(USER_KEY)
  }
}

function setSession(token, user) {
  authState.token = token
  authState.user = user
  persistAuth()
}

function clearSession() {
  authState.token = ''
  authState.user = null
  persistAuth()
}

async function register(payload) {
  const response = await http.post('/auth/register', payload)
  return response.data.data
}

async function login(payload) {
  const response = await http.post('/auth/login', payload)
  const session = response.data.data
  setSession(session.access_token, session.user)
  return session
}

async function fetchMe() {
  if (!authState.token) {
    return null
  }

  const response = await http.get('/auth/me')
  authState.user = response.data.data
  persistAuth()
  return authState.user
}

async function updateProfile(payload) {
  const response = await http.put('/auth/me', payload)
  authState.user = response.data.data
  persistAuth()
  return authState.user
}

async function logout() {
  if (authState.token) {
    try {
      await http.post('/auth/logout')
    } catch {
      // Ignore logout request failures and clear local session anyway.
    }
  }

  clearSession()
}

async function initializeAuth() {
  if (authState.initialized) {
    return
  }

  if (authState.token) {
    try {
      await fetchMe()
    } catch {
      clearSession()
    }
  }

  authState.initialized = true
}

export function useAuth() {
  return {
    authState,
    isAuthenticated: computed(() => Boolean(authState.token)),
    login,
    logout,
    register,
    fetchMe,
    updateProfile,
    initializeAuth,
    clearSession,
  }
}
