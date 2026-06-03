<template>
  <section class="page">
    <div class="panel">
      <h2>商品大厅</h2>
      <p class="muted-text">浏览在售商品，支持关键字搜索、分类筛选、价格区间筛选和排序。</p>
    </div>

    <div class="section-card">
      <div class="filter-grid">
        <label class="form-field">
          <span>关键字</span>
          <input v-model.trim="filters.keyword" type="search" placeholder="搜索标题或描述" @keyup.enter="loadProducts" />
        </label>
        <label class="form-field">
          <span>分类</span>
          <select v-model="filters.category_name">
            <option value="">全部分类</option>
            <option v-for="category in categories" :key="category.category_id" :value="category.category_name">
              {{ category.category_name }}
            </option>
          </select>
        </label>
        <label class="form-field">
          <span>最低价格</span>
          <input v-model="filters.min_price" min="0" type="number" placeholder="0" />
        </label>
        <label class="form-field">
          <span>最高价格</span>
          <input v-model="filters.max_price" min="0" type="number" placeholder="不限" />
        </label>
        <label class="form-field">
          <span>排序字段</span>
          <select v-model="filters.sort_by">
            <option value="publish_time">发布时间</option>
            <option value="price">价格</option>
          </select>
        </label>
        <label class="form-field">
          <span>排序方式</span>
          <select v-model="filters.sort_order">
            <option value="desc">降序</option>
            <option value="asc">升序</option>
          </select>
        </label>
      </div>
      <div class="form-actions">
        <button class="primary-btn" :disabled="loading" type="button" @click="loadProducts">
          {{ loading ? '查询中...' : '查询商品' }}
        </button>
        <button class="secondary-btn" type="button" @click="resetFilters">重置条件</button>
      </div>
    </div>

    <div class="table-card">
      <div class="table-header">
        <h3>商品列表</h3>
        <span class="muted-text">共 {{ products.length }} 件</span>
      </div>
      <p v-if="successMessage" class="form-success">{{ successMessage }}</p>
      <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
      <table class="data-table">
        <thead>
          <tr>
            <th>图片</th>
            <th>商品</th>
            <th>分类</th>
            <th>价格</th>
            <th>卖家</th>
            <th>状态</th>
            <th>交易地点</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.product_id">
            <td>
              <img class="product-thumb" :src="coverImage(product)" :alt="product.title" />
            </td>
            <td>
              <strong>{{ product.title }}</strong>
              <p class="table-subtitle">{{ product.description || '暂无描述' }}</p>
            </td>
            <td>{{ product.category_name }}</td>
            <td>{{ formatPrice(product.price) }}</td>
            <td>{{ product.seller_name }}</td>
            <td><span class="tag">{{ formatProductStatus(product.status) }}</span></td>
            <td>{{ product.trade_location }}</td>
            <td>
              <button
                class="primary-btn"
                :disabled="isSubmitting(product) || !canCreateOrder(product)"
                type="button"
                @click="handleCreateOrder(product)"
              >
                {{ isSubmitting(product) ? '下单中...' : orderButtonText(product) }}
              </button>
            </td>
          </tr>
          <tr v-if="!products.length && !loading">
            <td colspan="8" class="muted-text">暂无符合条件的商品</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { createOrder } from '../api/orders'
import { fetchCategories, fetchProducts } from '../api/products'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { authState } = useAuth()

const products = ref([])
const categories = ref([])
const loading = ref(false)
const submittingProductId = ref(null)
const successMessage = ref('')
const errorMessage = ref('')

const filters = reactive({
  keyword: '',
  category_name: '',
  min_price: '',
  max_price: '',
  sort_by: 'publish_time',
  sort_order: 'desc',
})

const isAuthenticated = computed(() => Boolean(authState.token))

function formatProductStatus(status) {
  return (
    {
      ON_SALE: '在售',
      LOCKED: '已锁定',
      SOLD: '已售出',
      OFFLINE: '已下架',
    }[status] || status
  )
}

function formatPrice(price) {
  return `${Number(price).toFixed(2)} 元`
}

function coverImage(product) {
  return product.image_urls?.[0] || 'https://dummyimage.com/120x90/e2e8f0/475569&text=SecondHand'
}

function buildQueryParams() {
  return Object.fromEntries(
    Object.entries(filters).filter(([, value]) => value !== '' && value !== null && value !== undefined),
  )
}

function canCreateOrder(product) {
  if (!isAuthenticated.value) {
    return false
  }
  if (authState.user?.user_id === product.seller_id) {
    return false
  }
  return product.status === 'ON_SALE'
}

function orderButtonText(product) {
  if (!isAuthenticated.value) {
    return '请先登录'
  }
  if (authState.user?.user_id === product.seller_id) {
    return '自己发布'
  }
  return product.status === 'ON_SALE' ? '立即下单' : '不可下单'
}

function isSubmitting(product) {
  return submittingProductId.value === product.product_id
}

async function loadCategories() {
  try {
    categories.value = await fetchCategories()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '获取分类列表失败'
  }
}

async function loadProducts() {
  loading.value = true
  errorMessage.value = ''
  try {
    products.value = await fetchProducts(buildQueryParams())
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '获取商品列表失败'
  } finally {
    loading.value = false
  }
}

async function resetFilters() {
  Object.assign(filters, {
    keyword: '',
    category_name: '',
    min_price: '',
    max_price: '',
    sort_by: 'publish_time',
    sort_order: 'desc',
  })
  await loadProducts()
}

async function handleCreateOrder(product) {
  successMessage.value = ''
  errorMessage.value = ''

  if (!isAuthenticated.value) {
    router.push({ path: '/login', query: { redirect: '/products' } })
    return
  }

  submittingProductId.value = product.product_id
  try {
    await createOrder({ product_id: product.product_id, buyer_note: '期待尽快线下交易' })
    successMessage.value = `已为商品“${product.title}”创建订单，请前往订单页继续操作。`
    await loadProducts()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '创建订单失败'
  } finally {
    submittingProductId.value = null
  }
}

onMounted(async () => {
  await Promise.all([loadCategories(), loadProducts()])
})
</script>
