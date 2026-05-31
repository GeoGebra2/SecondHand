import http from './http'

export async function fetchProducts() {
  const response = await http.get('/products')
  return response.data.data
}

export async function createProduct(payload) {
  const response = await http.post('/products', payload)
  return response.data.data
}
