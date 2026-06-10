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
        <p class="metric-value">12</p>
      </article>
      <article class="stats-card">
        <h3>系统总类别数</h3>
        <p>当前平台运营 of 商品分类</p>
        <p class="metric-value">{{ stats.categories?.length || 0 }}</p>
      </article>
      <article class="stats-card">
        <h3>今日推荐热度</h3>
        <p>系统计算的整体大屏活跃度</p>
        <p class="metric-value">高</p>
      </article>
    </div>

    <div class="grid-2">
      <article class="section-card">
        <h3>🔥 热门商品类别排行</h3>
        <p class="muted-text" style="font-size: 13px; margin-bottom: 15px;">基于后端聚合视图的实时统计</p>
        <div style="display: flex; flex-direction: column; gap: 15px;">
          <div v-for="item in stats.categories" :key="item.category_name" style="display: flex; align-items: center;">
            <span style="width: 80px; font-size: 14px; font-weight: bold;">{{ item.category_name }}</span>
            <div style="background: #f0f0f0; flex: 1; height: 16px; border-radius: 8px; margin: 0 12px; overflow: hidden;">
              <div :style="{ width: (item.sales_count * 5) + '%', background: 'linear-gradient(90deg, #42b983, #2cf598)', height: '100%', transition: 'width 0.8s ease' }"></div>
            </div>
            <span style="font-size: 13px; color: #666; width: 110px; text-align: right;">{{ item.sales_count }}热度值 (￥{{ item.total_revenue }})</span>
          </div>
        </div>
      </article>

      <article class="section-card">
        <h3>👑 活跃用户排行榜</h3>
        <ul class="list">
          <li v-for="(user, index) in stats.users" :key="user.user_name" style="padding: 12px 0; border-bottom: 1px dashed #eee;">
            🥇 <span style="color: #42b983; font-weight: bold;">Top {{ index + 1 }}</span>: {{ user.user_name }} 
            <span style="float: right; color: #999;">活跃贡献值: <strong style="color: #3b82f6;">{{ user.action_count }}</strong> 分</span>
          </li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 仅保留看板统计状态变量，移除了 notifications 变量
const stats = ref({ categories: [], users: [], trends: [] })

onMounted(async () => {
  try {
    // 仅调用后台统计分析大屏接口，彻底去除了消息接口调用
    const statsRes = await fetch('http://127.0.0.1:8000/my_task/stats/dashboard')
    const statsData = await statsRes.json()
    if (statsData.status === 'success') {
      stats.value = statsData
    }
  } catch (error) {
    console.error('获取后端数据失败，请确认后端 uvicorn 正在运行:', error)
  }
})
</script>