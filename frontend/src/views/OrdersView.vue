<template>
  <section class="page">
    <div class="panel">
      <h2>订单管理</h2>
      <p>这里预留买家订单、卖家订单、状态流转和评价入口。</p>
    </div>

    <div class="grid-2">
      <article class="todo-card">
        <h3>买家视角</h3>
        <ul class="list">
          <li>待确认订单</li>
          <li>待面交订单</li>
          <li>已完成订单</li>
          <li>评价入口</li>
        </ul>
      </article>

      <article class="todo-card">
        <h3>卖家视角</h3>
        <ul class="list">
          <li>新订单提醒</li>
          <li>确认成交</li>
          <li>取消记录</li>
          <li>历史成交归档</li>
        </ul>
      </article>
    </div>

    <div class="table-card">
      <h3>订单状态示例</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>订单编号</th>
            <th>商品</th>
            <th>买家</th>
            <th>卖家</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td>{{ order.id }}</td>
            <td>{{ order.product }}</td>
            <td>{{ order.buyer }}</td>
            <td>{{ order.seller }}</td>
            <td><span class="tag">{{ order.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
const orders = [
  { id: 'ORD-202605-001', product: '考研英语资料', buyer: '赵同学', seller: '陈同学', status: '待确认' },
  { id: 'ORD-202605-002', product: '平板支架', buyer: '钱同学', seller: '周同学', status: '交易中' },
  { id: 'ORD-202605-003', product: '宿舍小风扇', buyer: '孙同学', seller: '吴同学', status: '已完成' },
]
</script>
