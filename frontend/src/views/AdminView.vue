<template>
  <section class="page">
    <div class="panel">
      <h2>管理后台 & 信用风控中心</h2>
      <p class="muted-text">基于订单评分、接单后责任取消率、用户举报次数和交易活跃度生成信用等级与异常预警。</p>
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
            <th>状态</th>
            <th>计算分</th>
            <th>责任取消率</th>
            <th>卖家评分</th>
            <th>举报次数</th>
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
            <td><span class="tag" :class="statusTagClass(analysis.status)">{{ formatUserStatus(analysis.status) }}</span></td>
            <td>{{ analysis.computed_score }}</td>
            <td>{{ formatPercent(analysis.metrics.responsible_cancellation_rate) }}</td>
            <td>{{ analysis.metrics.average_seller_review_score ?? '暂无' }}</td>
            <td>{{ analysis.metrics.report_count }}</td>
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
            <td colspan="10" class="muted-text">暂无信用分析数据</td>
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
          <li>订单评分只计入卖家画像，低卖家评分会触发风险预警。</li>
          <li>卖家确认接单后，谁取消订单就计入谁的责任取消率。</li>
          <li>买家下单后、卖家接单前取消订单，不影响任何用户信用。</li>
          <li>举报次数独立统计，作为管理员拉黑处理的重要参考。</li>
          <li>商品发布数和订单参与度用于补充衡量活跃度与热度。</li>
        </ul>
      </article>
    </div>

    <div class="table-card">
      <div class="table-header">
        <h3>用户举报记录</h3>
        <span class="muted-text">共 {{ userReports.length }} 条</span>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>被举报用户</th>
            <th>举报人</th>
            <th>原因</th>
            <th>说明</th>
            <th>时间</th>
            <th>当前状态</th>
            <th>处理</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="report in userReports" :key="report.report_id">
            <td>
              <strong>{{ report.reported_user_name }}</strong>
              <p class="table-subtitle">ID: {{ report.reported_user_id }}</p>
            </td>
            <td>{{ report.reporter_name }}</td>
            <td>{{ report.reason }}</td>
            <td>{{ report.description || '无' }}</td>
            <td>{{ formatDate(report.create_time) }}</td>
            <td>
              <span class="tag" :class="statusTagClass(findUserStatus(report.reported_user_id))">
                {{ formatUserStatus(findUserStatus(report.reported_user_id)) }}
              </span>
            </td>
            <td>
              <div class="actions-cell">
                <button
                  v-if="findUserStatus(report.reported_user_id) !== 'blocked'"
                  class="secondary-btn"
                  type="button"
                  @click="handleBlockUser(report.reported_user_id)"
                >
                  拉黑
                </button>
                <button
                  v-else
                  class="secondary-btn"
                  type="button"
                  @click="handleUnblockUser(report.reported_user_id)"
                >
                  恢复
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!userReports.length && !loading">
            <td colspan="7" class="muted-text">暂无用户举报记录</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import {
  blockUser,
  fetchAdminDashboard,
  fetchCreditAnalysis,
  fetchUserReports,
  unblockUser,
} from '../api/admin'

const overviewCards = ref([])
const creditAnalyses = ref([])
const userReports = ref([])
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

function formatUserStatus(status) {
  return (
    {
      active: '正常',
      blocked: '已拉黑',
      disabled: '已禁用',
    }[status] || status || '未知'
  )
}

function statusTagClass(status) {
  return status === 'blocked' || status === 'disabled' ? 'tag-danger' : 'tag-incoming'
}

function findUserStatus(userId) {
  return creditAnalyses.value.find((item) => item.user_id === userId)?.status || '未知'
}

function formatDate(value) {
  if (!value) {
    return '-'
  }
  return new Date(value).toLocaleString()
}

async function loadDashboard() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [cards, analyses, reports] = await Promise.all([
      fetchAdminDashboard(),
      fetchCreditAnalysis(),
      fetchUserReports(),
    ])
    overviewCards.value = cards
    creditAnalyses.value = analyses
    userReports.value = reports
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '获取管理后台数据失败'
  } finally {
    loading.value = false
  }
}

async function handleBlockUser(userId) {
  errorMessage.value = ''
  try {
    await blockUser(userId)
    await loadDashboard()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '拉黑用户失败'
  }
}

async function handleUnblockUser(userId) {
  errorMessage.value = ''
  try {
    await unblockUser(userId)
    await loadDashboard()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '恢复用户失败'
  }
}

onMounted(loadDashboard)
</script>
