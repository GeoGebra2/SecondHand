import http from './http'

export async function fetchProducts(params = {}) {
  const response = await http.get('/products', { params })
  return response.data.data
}

export async function fetchMyProducts() {
  const response = await http.get('/products/mine')
  return response.data.data
}

export async function createProduct(payload) {
  const response = await http.post('/products', payload)
  return response.data.data
}

export async function updateProduct(productId, payload) {
  const response = await http.put(`/products/${productId}`, payload)
  return response.data.data
}

export async function offlineProduct(productId) {
  const response = await http.patch(`/products/${productId}/offline`)
  return response.data.data
}

export async function relistProduct(productId) {
  const response = await http.patch(`/products/${productId}/relist`)
  return response.data.data
}

export async function fetchCategories(params = {}) {
  const response = await http.get('/products/categories', { params })
  return response.data.data
}

export async function createCategory(payload) {
  const response = await http.post('/products/categories', payload)
  return response.data.data
}

export async function updateCategory(categoryId, payload) {
  const response = await http.put(`/products/categories/${categoryId}`, payload)
  return response.data.data
}
