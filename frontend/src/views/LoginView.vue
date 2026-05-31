<template>
  <section class="page auth-page">
    <div class="panel auth-panel">
      <div>
        <h2>账号登录</h2>
        <p class="muted-text">使用学号或邮箱登录校园二手交易平台。</p>
      </div>

      <form class="form-grid" @submit.prevent="handleLogin">
        <label class="form-field full-span">
          <span>学号或邮箱</span>
          <input v-model="form.account" type="text" placeholder="请输入学号或邮箱" />
        </label>

        <label class="form-field full-span">
          <span>密码</span>
          <input v-model="form.password" type="password" placeholder="请输入密码" />
        </label>

        <p v-if="errorMessage" class="form-error full-span">{{ errorMessage }}</p>

        <div class="form-actions full-span">
          <button class="primary-btn" :disabled="submitting" type="submit">
            {{ submitting ? '登录中...' : '立即登录' }}
          </button>
          <RouterLink class="secondary-link" to="/register">去注册</RouterLink>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuth } from '../composables/useAuth'

const route = useRoute()
const router = useRouter()
const { login } = useAuth()

const form = reactive({
  account: '',
  password: '',
})

const submitting = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''
  submitting.value = true

  try {
    await login(form)
    const redirectPath = route.query.redirect || '/profile'
    router.push(redirectPath)
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '登录失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>
