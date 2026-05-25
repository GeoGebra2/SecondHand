<template>
  <section class="page">
    <div class="panel">
      <h2>管理后台</h2>
      <p>这里用于展示商品审核、举报处理、统计分析和异常行为预警。</p>
    </div>

    <div class="grid-3">
      <article class="stats-card" v-for="metric in metrics" :key="metric.label">
        <h3>{{ metric.label }}</h3>
        <p>{{ metric.description }}</p>
        <p class="metric-value">{{ metric.value }}</p>
      </article>
    </div>

    <div class="grid-2">
      <article class="section-card">
        <h3>举报处理队列</h3>
        <ul class="list">
          <li>待审核商品举报</li>
          <li>虚假信息举报</li>
          <li>异常交易用户预警</li>
        </ul>
      </article>

      <article class="section-card">
        <h3>数据分析看板</h3>
        <ul class="list">
          <li>热门商品类别排行</li>
          <li>成交金额趋势</li>
          <li>活跃买家 / 卖家排行</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup>
const metrics = [
  { label: '待审核商品', description: '等待管理员确认上架的商品数量', value: '12' },
  { label: '待处理举报', description: '今日新增举报及历史未处理记录', value: '5' },
  { label: '活跃卖家', description: '近 7 天发布商品较多的用户数量', value: '28' },
]
</script>
