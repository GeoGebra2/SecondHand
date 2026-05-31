<template>
  <header class="app-header">
    <div>
      <h1 class="brand-title">校园二手交易平台</h1>
      <p class="brand-subtitle">课程展示版前端框架，覆盖用户、商品、订单和后台模块</p>
    </div>
    <div class="header-actions">
      <template v-if="authState.user">
        <span class="header-chip">当前用户：{{ authState.user.user_name }}</span>
        <RouterLink class="header-chip header-link" to="/profile">个人中心</RouterLink>
        <button class="header-chip header-button" type="button" @click="handleLogout">退出登录</button>
      </template>
      <template v-else>
        <RouterLink class="header-chip header-link" to="/login">登录</RouterLink>
        <RouterLink class="header-chip header-link" to="/register">注册</RouterLink>
      </template>
      <span class="header-chip">Vue 3</span>
      <span class="header-chip">FastAPI</span>
      <span class="header-chip">MySQL Ready</span>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'

import { useAuth } from '../../composables/useAuth'

const router = useRouter()
const { authState, logout } = useAuth()

async function handleLogout() {
  await logout()
  router.push('/login')
}
</script>
