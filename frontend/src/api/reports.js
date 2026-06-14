import http from './http'

export async function createUserReport(payload) {
  const response = await http.post('/reports/users', payload)
  return response.data.data
}
