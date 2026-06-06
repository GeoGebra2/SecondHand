<template>
  <section class="page">
    <div class="panel">
      <h2>商品大厅</h2>
      <p class="muted-text">浏览在售商品，并直接发起订单创建。下单后商品会进入锁定状态，等待卖家确认。</p>
    </div>

    <div class="grid-2">
      <article class="section-card">
        <h3>交易说明</h3>
        <ul class="list">
          <li>只有登录用户可创建订单。</li>
          <li>买家不能购买自己发布的商品。</li>
          <li>商品下单后会先锁定，避免重复购买。</li>
          <li>完成面交后请在订单页确认成交并评价。</li>
        </ul>
      </article>

      <article class="section-card">
        <h3>当前状态</h3>
        <p class="muted-text">演示账号可直接体验完整流程：浏览商品 -> 创建订单 -> 进入订单页跟进。</p>
        <p v-if="successMessage" class="form-success">{{ successMessage }}</p>
        <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
      </article>
    </div>

    <div class="table-card">
      <div class="table-header">
        <h3>商品列表</h3>
        <button class="secondary-btn" :disabled="loading" type="button" @click="loadProducts">
          {{ loading ? '刷新中...' : '刷新商品' }}
        </button>
      </div>
      <table class="data-table">
        <thead>
          <tr>
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
            <td>{{ product.title }}</td>
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

              <button
                class="secondary-btn"
                style="margin-left: 8px; background-color: #f59e0b; color: white; border: none;"
                type="button"
                @click="handleMyFavorite(product.product_id)"
              >
                ⭐ 收藏
              </button>
            </td>
          </tr>
          <tr v-if="!products.length && !loading">
            <td colspan="7" class="muted-text">暂无商品数据</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { createOrder } from '../api/orders'
import { fetchProducts } from '../api/products'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { authState } = useAuth()

const products = ref([])
const loading = ref(false)
const submittingProductId = ref(null)
const successMessage = ref('')
const errorMessage = ref('')

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

// 【新增：处理用户点击收藏按钮的逻辑】
// frontend/src/views/ProductsView.vue
async function handleMyFavorite(productId) {
  // 严格校验登录态
  if (!isAuthenticated.value || !authState.user?.user_id) {
    alert('提示：请先去登录您的个人账号再进行收藏！')
    router.push({ path: '/login', query: { redirect: '/products' } })
    return
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/my_task/favorite', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: authState.user.user_id, // 绝不硬编码，只用当前登录人的真实 ID
        product_id: productId
      })
    })
    const data = await response.json()
    if (data.status === 'success') {
      alert(`🌟 账号【${authState.user.user_name}】收藏成功！`)
    } else {
      alert('收藏失败：' + (data.detail || '您可能已经收藏过该商品'))
    }
  } catch (error) {
    alert('无法连接到后端，请确保 FastAPI 正在运行！')
  }
}

function formatPrice(price) {
  return `${Number(price).toFixed(2)} 元`
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

async function loadProducts() {
  loading.value = true
  errorMessage.value = ''
  try {
    products.value = await fetchProducts()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '获取商品列表失败'
  } finally {
    loading.value = false
  }
}

async function handleCreateOrder(product) {
  successMessage.value = ''
  errorMessage.value = ''

  if (!isAuthenticated.value) {
    router.push({ path: '/login', query: { redirect: '/products' } })
    return
  }

// 在点击某个购买意向或下单成功时，调用后端发送通知
async function triggerNotification(sellerId, productName) {
  await fetch('http://127.0.0.1:8000/my_task/notifications/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      receiver_id: sellerId, // 接收者是卖家
      content: `🔔 系统提醒：有同学对你发布的商品【${productName}】产生了购买意向，请及时处理！`
    })
  })
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

onMounted(loadProducts)
</script>
