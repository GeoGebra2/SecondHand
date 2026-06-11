import http from './http'

export async function createFavorite(payload) {
  const response = await http.post('/favorites', payload)
  return response.data.data
}

export async function fetchFavorites() {
  const response = await http.get('/favorites')
  return response.data.data
}

export async function fetchNotifications() {
  const response = await http.get('/notifications')
  return response.data.data
}

export async function createNotification(payload) {
  const response = await http.post('/notifications', payload)
  return response.data.data
}

export async function fetchAdminDashboard() {
  const response = await http.get('/admin/dashboard')
  return response.data.data
}
