import http from './http'

export async function fetchAdminDashboard() {
  const response = await http.get('/admin/dashboard')
  return response.data.data
}

export async function fetchCreditAnalysis() {
  const response = await http.get('/admin/credit-analysis')
  return response.data.data
}

export async function fetchUserReports() {
  const response = await http.get('/admin/reports')
  return response.data.data
}

export async function blockUser(userId) {
  const response = await http.patch(`/admin/users/${userId}/block`)
  return response.data.data
}

export async function unblockUser(userId) {
  const response = await http.patch(`/admin/users/${userId}/unblock`)
  return response.data.data
}
