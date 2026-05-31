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
        <p>当前平台运营的商品分类</p>
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
            <span style="font-size: 13px; color: #666; width: 110px; text-align: right;">{{ item.sales_count }}单 (￥{{ item.total_revenue }})</span>
          </div>
        </div>
      </article>

      <article class="section-card">
        <h3>👑 活跃用户排行榜</h3>
        <ul class="list" style="margin-bottom: 25px;">
          <li v-for="(user, index) in stats.users" :key="user.user_name" style="padding: 8px 0; border-bottom: 1px dashed #eee;">
            🥇 <span style="color: #42b983; font-weight: bold;">Top {{ index + 1 }}</span>: {{ user.user_name }} 
            <span style="float: right; color: #999;">互动 {{ user.action_count }} 次</span>
          </li>
        </ul>

        <h3>🔔 站内消息实时提醒 (用户ID: 1)</h3>
        <div v-if="notifications.length === 0" style="color: #bbb; text-align: center; padding: 15px;">暂无新通知</div>
        <div v-for="msg in notifications" :key="msg.msg_id" style="background: #f4f7ff; padding: 10px; border-left: 4px solid #3b82f6; margin-top: 10px; border-radius: 0 4px 4px 0;">
          <p style="margin: 0; font-size: 14px; color: #333;">{{ msg.content }}</p>
          <small style="color: #999; font-size: 11px;">时间: {{ new Date(msg.create_time).toLocaleString() }}</small>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const stats = ref({ categories: [], users: [], trends: [] })
const notifications = ref([])

onMounted(async () => {
  try {
    // 1. 调用你跑通的后台统计分析大屏接口
    const statsRes = await fetch('http://127.0.0.1:8000/my_task/stats/dashboard')
    const statsData = await statsRes.json()
    if (statsData.status === 'success') {
      stats.value = statsData
    }

    // 2. 调用你跑通的消息提醒接口，默认获取用户1的未读消息
    const notifyRes = await fetch('http://127.0.0.1:8000/my_task/notifications/1')
    const notifyData = await notifyRes.json()
    if (notifyData.status === 'success') {
      notifications.value = notifyData.data
    }
  } catch (error) {
    console.error('获取后端数据失败，请确认后端 uvicorn 正在运行:', error)
  }
})
</script>