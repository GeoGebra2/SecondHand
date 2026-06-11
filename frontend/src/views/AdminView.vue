<template>
  <section class="page">
    <div class="panel">
      <h2>管理后台 & 信用风控中心</h2>
      <p class="muted-text">基于订单完成率、取消率、评价分数、商品发布活跃度和交易活跃度生成信用等级与异常预警。</p>
    </div>

    <div class="grid-3">
      <article class="stats-card" v-for="card in overviewCards" :key="card.label">
        <h3>{{ card.label }}</h3>
        <p>{{ card.description }}</p>
        <p class="metric-value">{{ card.value }}</p>
      </article>
    </div>

    <div class="grid-3">
      <article class="stats-card">
        <h3>已分析用户</h3>
        <p>纳入信用计算的账号数量</p>
        <p class="metric-value">{{ creditAnalyses.length }}</p>
      </article>
      <article class="stats-card">
        <h3>异常预警</h3>
        <p>中高风险或存在异常原因的账号</p>
        <p class="metric-value">{{ suspiciousUsers.length }}</p>
      </article>
      <article class="stats-card">
        <h3>平均信用分</h3>
        <p>按多维交易行为加权计算</p>
        <p class="metric-value">{{ averageCreditScore }}</p>
      </article>
    </div>

    <div class="table-card">
      <div class="table-header">
        <h3>用户信用评估</h3>
        <button class="secondary-btn" :disabled="loading" type="button" @click="loadDashboard">
          {{ loading ? '刷新中...' : '刷新分析' }}
        </button>
      </div>
      <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
      <table class="data-table">
        <thead>
          <tr>
            <th>用户</th>
            <th>信用等级</th>
            <th>风险等级</th>
            <th>计算分</th>
            <th>完成率</th>
            <th>取消率</th>
            <th>评价均分</th>
            <th>活跃度</th>
            <th>预警原因</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="analysis in creditAnalyses" :key="analysis.user_id">
            <td>
              <strong>{{ analysis.user_name }}</strong>
              <p class="table-subtitle">{{ analysis.email }}</p>
            </td>
            <td><span class="tag">{{ analysis.credit_level }}</span></td>
            <td>
              <span class="tag" :class="riskTagClass(analysis.risk_level)">
                {{ formatRiskLevel(analysis.risk_level) }}
              </span>
            </td>
            <td>{{ analysis.computed_score }}</td>
            <td>{{ formatPercent(analysis.metrics.completion_rate) }}</td>
            <td>{{ formatPercent(analysis.metrics.cancellation_rate) }}</td>
            <td>{{ analysis.metrics.average_review_score ?? '暂无' }}</td>
            <td>{{ analysis.metrics.activity_score }}</td>
            <td>
              <span v-if="!analysis.warning_reasons.length" class="muted-text">无</span>
              <div v-else class="review-list">
                <span v-for="reason in analysis.warning_reasons" :key="reason" class="tag tag-outgoing">
                  {{ reason }}
                </span>
              </div>
            </td>
          </tr>
          <tr v-if="!creditAnalyses.length && !loading">
            <td colspan="9" class="muted-text">暂无信用分析数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="grid-2">
      <article class="section-card">
        <h3>异常账号清单</h3>
        <ul class="list">
          <li v-for="user in suspiciousUsers" :key="user.user_id">
            {{ user.user_name }}：{{ user.warning_reasons.join('、') }}
          </li>
          <li v-if="!suspiciousUsers.length">当前没有中高风险账号</li>
        </ul>
      </article>

      <article class="section-card">
        <h3>评分规则摘要</h3>
        <ul class="list">
          <li>完成率权重 35%，取消率权重 25%。</li>
          <li>评价均分权重 25%，无评价时按默认中高水平计入。</li>
          <li>商品发布数和订单参与度用于衡量活跃度与热度。</li>
          <li>高取消率、低完成率、低评价、订单堆积会触发异常预警。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import { fetchAdminDashboard, fetchCreditAnalysis } from '../api/admin'

const overviewCards = ref([])
const creditAnalyses = ref([])
const loading = ref(false)
const errorMessage = ref('')

const suspiciousUsers = computed(() => creditAnalyses.value.filter((item) => item.is_suspicious))
const averageCreditScore = computed(() => {
  if (!creditAnalyses.value.length) {
    return 0
  }
  const totalScore = creditAnalyses.value.reduce((sum, item) => sum + item.computed_score, 0)
  return Math.round(totalScore / creditAnalyses.value.length)
})

function formatPercent(value) {
  return `${Math.round(Number(value) * 100)}%`
}

function formatRiskLevel(level) {
  return (
    {
      LOW: '低风险',
      MEDIUM: '中风险',
      HIGH: '高风险',
    }[level] || level
  )
}

function riskTagClass(level) {
  return (
    {
      LOW: 'tag-incoming',
      MEDIUM: 'tag-warning',
      HIGH: 'tag-danger',
    }[level] || ''
  )
}

async function loadDashboard() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [cards, analyses] = await Promise.all([fetchAdminDashboard(), fetchCreditAnalysis()])
    overviewCards.value = cards
    creditAnalyses.value = analyses
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '获取管理后台数据失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>
