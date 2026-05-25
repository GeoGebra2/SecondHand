<template>
  <aside class="app-sidebar">
    <h2 class="sidebar-title">功能导航</h2>
    <nav class="sidebar-menu">
      <RouterLink
        v-for="item in menuItems"
        :key="item.to"
        :to="item.to"
        class="nav-link"
        active-class="is-active"
      >
        {{ item.label }}
      </RouterLink>
    </nav>
  </aside>
</template>

<script setup>
const menuItems = [
  { label: '平台总览', to: '/' },
  { label: '商品大厅', to: '/products' },
  { label: '发布中心', to: '/publish' },
  { label: '订单管理', to: '/orders' },
  { label: '管理后台', to: '/admin' },
]
</script>
