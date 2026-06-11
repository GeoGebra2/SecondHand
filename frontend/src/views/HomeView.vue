<template>
  <section class="page">
    <div class="hero">
      <div class="section-card">
        <h2>智能推荐中枢</h2>
        <p>
          系统结合用户收藏记录、浏览偏好、下单行为、商品类别偏好和平台热度，
          通过轻量级 AI 分析模型生成“猜你喜欢”推荐结果，并输出可解释推荐理由。
        </p>
        <ul class="list">
          <li>行为特征：收藏、浏览、购买、价格区间</li>
          <li>协同偏好：相似兴趣用户行为加权</li>
          <li>热度分析：收藏量、成交量、发布时间综合评分</li>
        </ul>
      </div>
      <div class="stats-card">
        <h3>推荐模型</h3>
        <p>{{ recommendation.algorithm || 'hybrid-ai-lite-v1' }}</p>
        <p class="metric-value">AI Ready</p>
      </div>
    </div>

    <div class="section-card">
      <div class="table-header">
        <h3>猜你喜欢</h3>
        <button class="secondary-btn" :disabled="loading" type="button" @click="loadRecommendations">
          {{ loading ? '生成中...' : '刷新推荐' }}
        </button>
      </div>
      <p class="muted-text">{{ recommendation.profile_summary || '系统将根据行为数据生成个性化推荐。' }}</p>
      <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
      <div class="grid-3" style="margin-top: 18px;">
        <article v-for="item in recommendation.items" :key="item.product_id" class="module-card">
          <img
            class="product-thumb large-thumb"
            :src="item.image_urls?.[0] || 'https://dummyimage.com/320x200/e2e8f0/475569&text=SecondHand'"
            :alt="item.title"
            style="width: 100%; height: 180px; object-fit: cover; border-radius: 10px;"
          />
          <span class="tag" style="margin-top: 12px;">{{ item.category_name }}</span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description || '暂无描述' }}</p>
          <p class="muted-text">AI 推荐分：{{ item.ai_score.toFixed(3) }}</p>
          <p class="muted-text">推荐理由：{{ item.ai_reason }}</p>
          <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px;">
            <span v-for="tag in item.ai_tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <div class="form-actions" style="margin-top: 14px;">
            <router-link class="primary-btn" to="/products">去商品大厅</router-link>
          </div>
        </article>
      </div>
      <p v-if="!recommendation.items.length && !loading" class="muted-text" style="margin-top: 16px;">
        暂无推荐结果，请先登录并进行收藏、浏览或下单操作。
      </p>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'

import { fetchRecommendations } from '../api/products'

const loading = ref(false)
const errorMessage = ref('')
const recommendation = ref({
  algorithm: '',
  profile_summary: '',
  items: [],
})

async function loadRecommendations() {
  loading.value = true
  errorMessage.value = ''
  try {
    recommendation.value = await fetchRecommendations()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '获取智能推荐失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadRecommendations)
</script>
