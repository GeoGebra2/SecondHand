<template>
  <section class="page">
    <div class="hero">
      <div class="section-card">
        <h2>项目总览</h2>
        <p>
          这个框架围绕课程报告中的六大能力展开：用户管理、商品管理、交易管理、评价举报、推荐分析和后台治理。
          目前页面以结构展示为主，方便后续逐个填充真实业务逻辑。
        </p>
        <ul class="list">
          <li>支持前后端分离演示</li>
          <li>页面布局已按课程答辩常见模块拆分</li>
          <li>后端已预留统一 API 和统计接口骨架</li>
        </ul>
      </div>
      <div class="stats-card">
        <h3>阶段状态</h3>
        <p>框架搭建完成后，可继续对接数据库和接口联调。</p>
        <p class="metric-value">MVP Ready</p>
      </div>
    </div>

    <div class="grid-3">
      <article class="module-card" v-for="item in highlights" :key="item.title">
        <span class="tag">{{ item.tag }}</span>
        <h3>{{ item.title }}</h3>
        <p>{{ item.description }}</p>
      </article>
    </div>
  </section>
</template>

<script setup>
const highlights = [
  {
    tag: '用户',
    title: '用户与信用体系',
    description: '预留注册登录、校园认证、信誉分展示和个人中心入口。',
  },
  {
    tag: '商品',
    title: '商品与分类管理',
    description: '预留商品发布、分类筛选、状态管理和图片展示区域。',
  },
  {
    tag: '数据',
    title: '统计与推荐分析',
    description: '预留热门类别、成交走势和异常交易预警的展示模块。',
  },
]
</script>
