import http from './http'

export async function fetchOrders() {
  const response = await http.get('/orders')
  return response.data.data
}

export async function createOrder(payload) {
  const response = await http.post('/orders', payload)
  return response.data.data
}

export async function confirmOrder(orderId) {
  const response = await http.patch(`/orders/${orderId}/confirm`)
  return response.data.data
}

export async function completeOrder(orderId) {
  const response = await http.patch(`/orders/${orderId}/complete`)
  return response.data.data
}

export async function cancelOrder(orderId, payload) {
  const response = await http.patch(`/orders/${orderId}/cancel`, payload)
  return response.data.data
}
