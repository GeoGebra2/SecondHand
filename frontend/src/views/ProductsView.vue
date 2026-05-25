<template>
  <section class="page">
    <div class="panel">
      <h2>商品大厅</h2>
      <p>这里预留商品搜索、分类筛选、排序和商品卡片列表区域。</p>
    </div>

    <div class="grid-2">
      <article class="section-card">
        <h3>筛选区域</h3>
        <ul class="list">
          <li>关键字搜索</li>
          <li>商品分类筛选</li>
          <li>价格区间筛选</li>
          <li>发布时间 / 热度排序</li>
        </ul>
      </article>

      <article class="section-card">
        <h3>推荐区域</h3>
        <ul class="list">
          <li>猜你喜欢</li>
          <li>近期热门</li>
          <li>收藏较多商品</li>
        </ul>
      </article>
    </div>

    <div class="table-card">
      <h3>商品列表示例</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>商品</th>
            <th>分类</th>
            <th>价格</th>
            <th>卖家</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.title">
            <td>{{ product.title }}</td>
            <td>{{ product.category }}</td>
            <td>{{ product.price }}</td>
            <td>{{ product.seller }}</td>
            <td><span class="tag">{{ product.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
const products = [
  { title: '高等数学教材', category: '教材资料', price: '25 元', seller: '张同学', status: '在售' },
  { title: '二手机械键盘', category: '数码产品', price: '120 元', seller: '李同学', status: '待面交' },
  { title: '宿舍折叠自行车', category: '生活用品', price: '260 元', seller: '王同学', status: '已收藏' },
]
</script>
