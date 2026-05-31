<template>
  <aside class="app-sidebar">
    <h2 class="sidebar-title">功能导航</h2>
    <nav class="sidebar-menu">
      <RouterLink
        v-for="item in visibleMenuItems"
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
import { computed } from 'vue'

import { useAuth } from '../../composables/useAuth'

const { authState } = useAuth()

const menuItems = [
  { label: '平台总览', to: '/' },
  { label: '商品大厅', to: '/products' },
  { label: '登录', to: '/login', guestOnly: true },
  { label: '注册', to: '/register', guestOnly: true },
  { label: '个人中心', to: '/profile', requiresAuth: true },
  { label: '发布中心', to: '/publish', requiresAuth: true },
  { label: '订单管理', to: '/orders', requiresAuth: true },
  { label: '管理后台', to: '/admin', requiresAdmin: true },
]

const visibleMenuItems = computed(() =>
  menuItems.filter((item) => {
    if (item.requiresAdmin) {
      return authState.user?.role === 'admin'
    }
    if (item.requiresAuth) {
      return Boolean(authState.token)
    }
    if (item.guestOnly) {
      return !authState.token
    }
    return true
  })
)
</script>
