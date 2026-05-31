import http from './http'

export async function createReview(payload) {
  const response = await http.post('/reviews', payload)
  return response.data.data
}

export async function fetchOrderReviews(orderId) {
  const response = await http.get(`/reviews/order/${orderId}`)
  return response.data.data
}
