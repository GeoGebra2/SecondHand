import http from './http'

export async function fetchAdminDashboard() {
  const response = await http.get('/admin/dashboard')
  return response.data.data
}

export async function fetchCreditAnalysis() {
  const response = await http.get('/admin/credit-analysis')
  return response.data.data
}
