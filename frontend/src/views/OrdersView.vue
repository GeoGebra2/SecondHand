<template>
  <section class="page">
    <div class="panel">
      <h2>订单管理</h2>
      <p class="muted-text">跟进买卖双方的订单状态，并在成交后提交评价反馈。</p>
    </div>

    <div class="grid-2">
      <article class="todo-card">
        <h3>买家视角</h3>
        <ul class="list">
          <li>创建订单后等待卖家确认。</li>
          <li>卖家确认后进入交易中状态。</li>
          <li>面交完成后由买家确认成交。</li>
          <li>完成订单后可对卖家进行一次评价。</li>
        </ul>
      </article>

      <article class="todo-card">
        <h3>卖家视角</h3>
        <ul class="list">
          <li>待确认订单需要卖家手动接单。</li>
          <li>若交易取消，商品会重新回到在售状态。</li>
          <li>已完成订单会进入历史成交记录。</li>
          <li>订单状态与商品状态会同步更新。</li>
        </ul>
      </article>
    </div>

    <div class="table-card">
      <div class="table-header">
        <h3>订单列表</h3>
        <button class="secondary-btn" :disabled="loading" type="button" @click="loadOrders">
          {{ loading ? '刷新中...' : '刷新订单' }}
        </button>
      </div>
      <p v-if="successMessage" class="form-success">{{ successMessage }}</p>
      <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>

      <table class="data-table">
        <thead>
          <tr>
            <th>订单编号</th>
            <th>商品</th>
            <th>交易角色</th>
            <th>对方用户</th>
            <th>金额</th>
            <th>状态</th>
            <th>交易地点</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.order_id">
            <td>#{{ order.order_id }}</td>
            <td>{{ order.product_title }}</td>
            <td>{{ order.buyer_id === authState.user?.user_id ? '买家' : '卖家' }}</td>
            <td>{{ counterpartName(order) }}</td>
            <td>{{ formatPrice(order.order_amount) }}</td>
            <td><span class="tag">{{ formatOrderStatus(order.order_status) }}</span></td>
            <td>{{ order.trade_location }}</td>
            <td class="actions-cell">
              <button
                v-if="canConfirm(order)"
                class="primary-btn"
                :disabled="isWorking(order.order_id)"
                type="button"
                @click="handleConfirm(order.order_id)"
              >
                {{ isWorking(order.order_id) ? '处理中...' : '确认接单' }}
              </button>
              <button
                v-if="canComplete(order)"
                class="primary-btn"
                :disabled="isWorking(order.order_id)"
                type="button"
                @click="handleComplete(order.order_id)"
              >
                {{ isWorking(order.order_id) ? '处理中...' : '确认成交' }}
              </button>
              <button
                v-if="canCancel(order)"
                class="secondary-btn"
                :disabled="isWorking(order.order_id)"
                type="button"
                @click="handleCancel(order.order_id)"
              >
                {{ isWorking(order.order_id) ? '处理中...' : '取消订单' }}
              </button>
              <span v-if="!hasAvailableAction(order)" class="muted-text">无可执行操作</span>
            </td>
          </tr>
          <tr v-if="!orders.length && !loading">
            <td colspan="8" class="muted-text">当前没有订单记录</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="grid-2">
      <article class="section-card">
        <h3>待评价订单</h3>
        <div v-if="reviewableOrders.length" class="review-list">
          <button
            v-for="order in reviewableOrders"
            :key="order.order_id"
            class="secondary-btn"
            type="button"
            @click="selectReviewOrder(order)"
          >
            订单 #{{ order.order_id }} - {{ order.product_title }}
          </button>
        </div>
        <p v-else class="muted-text">暂无待评价订单。</p>
      </article>

      <article class="section-card">
        <h3>评价反馈</h3>
        <form class="form-grid" @submit.prevent="handleReview">
          <label class="form-field full-span">
            <span>当前订单</span>
            <input :value="selectedReviewOrderLabel" disabled type="text" />
          </label>

          <label class="form-field">
            <span>评分</span>
            <select v-model.number="reviewForm.score" :disabled="!selectedReviewOrder">
              <option :value="5">5 分</option>
              <option :value="4">4 分</option>
              <option :value="3">3 分</option>
              <option :value="2">2 分</option>
              <option :value="1">1 分</option>
            </select>
          </label>

          <label class="form-field full-span">
            <span>评价内容</span>
            <textarea
              v-model="reviewForm.content"
              :disabled="!selectedReviewOrder"
              rows="4"
              placeholder="请输入交易体验和卖家表现"
            ></textarea>
          </label>

          <div class="form-actions full-span">
            <button
              class="primary-btn"
              :disabled="reviewSubmitting || !selectedReviewOrder"
              type="submit"
            >
              {{ reviewSubmitting ? '提交中...' : '提交评价' }}
            </button>
          </div>
        </form>
      </article>
    </div>

    <div class="table-card">
      <h3>已提交评价</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>订单编号</th>
            <th>商品</th>
            <th>评价关系</th>
            <th>评价人</th>
            <th>评价对象</th>
            <th>评分</th>
            <th>评价内容</th>
            <th>提交时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="review in reviews" :key="review.review_id">
            <td>#{{ review.order_id }}</td>
            <td>{{ review.product_title }}</td>
            <td>
              <span class="tag" :class="reviewRelationClass(review)">
                {{ reviewRelationLabel(review) }}
              </span>
            </td>
            <td>{{ review.reviewer_name }}</td>
            <td>{{ review.reviewed_user_name }}</td>
            <td>{{ review.score }} 分</td>
            <td>{{ review.content }}</td>
            <td>{{ formatDate(review.create_time) }}</td>
          </tr>
          <tr v-if="!reviews.length">
            <td colspan="8" class="muted-text">暂无评价记录</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import { cancelOrder, completeOrder, confirmOrder, fetchOrders } from '../api/orders'
import { createReview, fetchOrderReviews } from '../api/reviews'
import { useAuth } from '../composables/useAuth'

const { authState } = useAuth()

const orders = ref([])
const reviews = ref([])
const loading = ref(false)
const workingOrderId = ref(null)
const reviewSubmitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const selectedReviewOrder = ref(null)

const reviewForm = reactive({
  score: 5,
  content: '',
})

const reviewableOrders = computed(() => orders.value.filter((order) => order.can_review))
const selectedReviewOrderLabel = computed(() =>
  selectedReviewOrder.value
    ? `#${selectedReviewOrder.value.order_id} - ${selectedReviewOrder.value.product_title} - 评价卖家 ${selectedReviewOrder.value.seller_name}`
    : '请先从左侧选择待评价订单'
)

function formatOrderStatus(status) {
  return (
    {
      PENDING: '待确认',
      IN_PROGRESS: '交易中',
      COMPLETED: '已完成',
      CANCELLED: '已取消',
    }[status] || status
  )
}

function formatPrice(value) {
  return `${Number(value).toFixed(2)} 元`
}

function formatDate(value) {
  if (!value) {
    return '-'
  }
  return new Date(value).toLocaleString('zh-CN')
}

function counterpartName(order) {
  return order.buyer_id === authState.user?.user_id ? order.seller_name : order.buyer_name
}

function reviewRelationLabel(review) {
  if (review.reviewer_id === authState.user?.user_id) {
    return '我给对方'
  }
  if (review.reviewed_user_id === authState.user?.user_id) {
    return '对方给我'
  }
  return '订单评价'
}

function reviewRelationClass(review) {
  if (review.reviewer_id === authState.user?.user_id) {
    return 'tag-outgoing'
  }
  if (review.reviewed_user_id === authState.user?.user_id) {
    return 'tag-incoming'
  }
  return ''
}

function canConfirm(order) {
  return order.seller_id === authState.user?.user_id && order.order_status === 'PENDING'
}

function canComplete(order) {
  return order.buyer_id === authState.user?.user_id && order.order_status === 'IN_PROGRESS'
}

function canCancel(order) {
  return (
    [order.buyer_id, order.seller_id].includes(authState.user?.user_id) &&
    !['COMPLETED', 'CANCELLED'].includes(order.order_status)
  )
}

function hasAvailableAction(order) {
  return canConfirm(order) || canComplete(order) || canCancel(order)
}

function isWorking(orderId) {
  return workingOrderId.value === orderId
}

function selectReviewOrder(order) {
  selectedReviewOrder.value = order
  reviewForm.score = 5
  reviewForm.content = ''
}

async function loadReviews() {
  const completedOrders = orders.value.filter((order) => order.order_status === 'COMPLETED')
  const reviewResponses = await Promise.all(
    completedOrders.map(async (order) => {
      const orderReviews = await fetchOrderReviews(order.order_id)
      return orderReviews.map((review) => ({
        ...review,
        product_title: order.product_title,
      }))
    })
  )
  reviews.value = reviewResponses
    .flat()
    .sort((left, right) => new Date(right.create_time) - new Date(left.create_time))
}

async function loadOrders(options = {}) {
  loading.value = true
  errorMessage.value = ''
  if (!options.preserveSuccessMessage) {
    successMessage.value = ''
  }
  try {
    orders.value = await fetchOrders()
    await loadReviews()
    if (!selectedReviewOrder.value) {
      const nextReviewOrder = reviewableOrders.value[0]
      if (nextReviewOrder) {
        selectReviewOrder(nextReviewOrder)
      }
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '获取订单列表失败'
  } finally {
    loading.value = false
  }
}

async function executeOrderAction(orderId, action, successText) {
  successMessage.value = ''
  errorMessage.value = ''
  workingOrderId.value = orderId
  try {
    await action()
    await loadOrders({ preserveSuccessMessage: true })
    successMessage.value = successText
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '订单操作失败'
  } finally {
    workingOrderId.value = null
  }
}

function handleConfirm(orderId) {
  return executeOrderAction(orderId, () => confirmOrder(orderId), '卖家已确认订单，当前状态为交易中。')
}

function handleComplete(orderId) {
  return executeOrderAction(orderId, () => completeOrder(orderId), '买家已确认成交，订单已完成。')
}

function handleCancel(orderId) {
  return executeOrderAction(
    orderId,
    () => cancelOrder(orderId, { cancel_reason: '演示取消订单' }),
    '订单已取消，商品已恢复在售状态。'
  )
}

async function handleReview() {
  if (!selectedReviewOrder.value) {
    errorMessage.value = '请先选择待评价订单'
    return
  }

  successMessage.value = ''
  errorMessage.value = ''
  reviewSubmitting.value = true
  try {
    await createReview({
      order_id: selectedReviewOrder.value.order_id,
      score: reviewForm.score,
      content: reviewForm.content,
    })
    successMessage.value = '评价提交成功，卖家信誉分已同步更新。'
    selectedReviewOrder.value = null
    reviewForm.score = 5
    reviewForm.content = ''
    await loadOrders({ preserveSuccessMessage: true })
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '评价提交失败'
  } finally {
    reviewSubmitting.value = false
  }
}

onMounted(loadOrders)
</script>
