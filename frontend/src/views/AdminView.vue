<template>
  <section class="page">
    <div class="panel">
      <h2>管理后台 & 数据统计中心</h2>
      <p>这里用于展示真实的商品分类销量、活跃用户统计以及系统运行状态。</p>
    </div>

    <div class="grid-3">
      <article class="stats-card">
        <h3>待审核商品</h3>
        <p>等待管理员确认上架的数量</p>
        <p class="metric-value">{{ stats.pending_product_count }}</p>
      </article>
      <article class="stats-card">
        <h3>系统总类别数</h3>
        <p>当前平台启用中的商品分类数量</p>
        <p class="metric-value">{{ stats.category_count }}</p>
      </article>
      <article class="stats-card">
        <h3>今日推荐热度</h3>
        <p>系统计算的整体大屏活跃度</p>
        <p class="metric-value">{{ stats.recommendation_heat }}</p>
      </article>
    </div>

    <div class="grid-2">
      <article class="section-card">
        <h3>热门商品类别排行</h3>
        <p class="muted-text" style="font-size: 13px; margin-bottom: 15px;">基于后端聚合统计的实时结果</p>
        <div style="display: flex; flex-direction: column; gap: 15px;">
          <div v-for="item in stats.categories" :key="item.category_id" style="display: flex; align-items: center;">
            <span style="width: 80px; font-size: 14px; font-weight: bold;">{{ item.category_name }}</span>
            <div style="background: #f0f0f0; flex: 1; height: 16px; border-radius: 8px; margin: 0 12px; overflow: hidden;">
              <div :style="{ width: (item.sales_count * 5) + '%', background: 'linear-gradient(90deg, #42b983, #2cf598)', height: '100%', transition: 'width 0.8s ease' }"></div>
            </div>
            <span style="font-size: 13px; color: #666; width: 110px; text-align: right;">{{ item.sales_count }} 热度值 (￥{{ item.total_revenue }})</span>
          </div>
        </div>
      </article>

      <article class="section-card">
        <h3>活跃用户排行榜</h3>
        <ul class="list">
          <li v-for="(user, index) in stats.users" :key="user.user_name" style="padding: 12px 0; border-bottom: 1px dashed #eee;">
            Top {{ index + 1 }}: {{ user.user_name }}
            <span style="float: right; color: #999;">活跃贡献值: <strong style="color: #3b82f6;">{{ user.action_count }}</strong> 分</span>
          </li>
        </ul>
      </article>
    </div>

    <div class="table-card">
      <div class="table-header">
        <h3>用户信用评估</h3>
        <button class="secondary-btn" :disabled="loading" type="button" @click="loadAdminData">
          {{ loading ? '刷新中...' : '刷新分析' }}
        </button>
      </div>
      <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
      <table class="data-table">
        <thead>
          <tr>
            <th>用户</th>
            <th>状态</th>
            <th>信用等级</th>
            <th>风险等级</th>
            <th>计算分</th>
            <th>责任取消率</th>
            <th>卖家评分</th>
            <th>举报次数</th>
            <th>预警原因</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="analysis in creditAnalyses" :key="analysis.user_id">
            <td>
              <strong>{{ analysis.user_name }}</strong>
              <p class="table-subtitle">{{ analysis.email }}</p>
            </td>
            <td><span class="tag" :class="statusTagClass(analysis.status)">{{ formatUserStatus(analysis.status) }}</span></td>
            <td><span class="tag">{{ analysis.credit_level }}</span></td>
            <td><span class="tag" :class="riskTagClass(analysis.risk_level)">{{ formatRiskLevel(analysis.risk_level) }}</span></td>
            <td>{{ analysis.computed_score }}</td>
            <td>{{ formatPercent(analysis.metrics.responsible_cancellation_rate) }}</td>
            <td>{{ analysis.metrics.average_seller_review_score ?? '暂无' }}</td>
            <td>{{ analysis.metrics.report_count }}</td>
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
import { onMounted, ref } from 'vue'

import { blockUser, fetchAdminDashboard, fetchCreditAnalysis, fetchUserReports, unblockUser } from '../api/admin'

const stats = ref({
  pending_product_count: 0,
  category_count: 0,
  recommendation_heat: '中',
  categories: [],
  users: [],
  trends: [],
})
const creditAnalyses = ref([])
const userReports = ref([])
const loading = ref(false)
const errorMessage = ref('')

function formatPercent(value) {
  return `${Math.round(Number(value || 0) * 100)}%`
}

function formatRiskLevel(level) {
  return ({ LOW: '低风险', MEDIUM: '中风险', HIGH: '高风险' }[level] || level || '-')
}

function riskTagClass(level) {
  return ({ LOW: 'tag-incoming', MEDIUM: 'tag-warning', HIGH: 'tag-danger' }[level] || '')
}

function formatUserStatus(status) {
  return ({ active: '正常', blocked: '已拉黑', disabled: '已禁用' }[status] || status || '未知')
}

function statusTagClass(status) {
  return status === 'blocked' || status === 'disabled' ? 'tag-danger' : 'tag-incoming'
}

function findUserStatus(userId) {
  return creditAnalyses.value.find((item) => item.user_id === userId)?.status || '未知'
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString('zh-CN') : '-'
}

async function loadAdminData() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [dashboard, analyses, reports] = await Promise.all([
      fetchAdminDashboard(),
      fetchCreditAnalysis(),
      fetchUserReports(),
    ])
    stats.value = dashboard
    creditAnalyses.value = analyses
    userReports.value = reports
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '获取后端数据失败，请确认后端 uvicorn 正在运行'
  } finally {
    loading.value = false
  }
}

async function handleBlockUser(userId) {
  try {
    await blockUser(userId)
    await loadAdminData()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '拉黑用户失败'
  }
}

async function handleUnblockUser(userId) {
  try {
    await unblockUser(userId)
    await loadAdminData()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '恢复用户失败'
  }
}

onMounted(loadAdminData)
</script>
