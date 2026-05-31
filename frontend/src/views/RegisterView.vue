<template>
  <section class="page auth-page">
    <div class="panel auth-panel">
      <div>
        <h2>用户注册</h2>
        <p class="muted-text">完成学号实名登记后即可登录和维护个人资料。</p>
      </div>

      <form class="form-grid" @submit.prevent="handleRegister">
        <label class="form-field">
          <span>学号</span>
          <input v-model="form.student_no" type="text" placeholder="请输入学号" />
        </label>

        <label class="form-field">
          <span>姓名/昵称</span>
          <input v-model="form.user_name" type="text" placeholder="请输入姓名或昵称" />
        </label>

        <label class="form-field">
          <span>邮箱</span>
          <input v-model="form.email" type="email" placeholder="请输入邮箱" />
        </label>

        <label class="form-field">
          <span>手机号</span>
          <input v-model="form.phone" type="text" placeholder="请输入手机号" />
        </label>

        <label class="form-field">
          <span>密码</span>
          <input v-model="form.password" type="password" placeholder="至少 8 位密码" />
        </label>

        <label class="form-field">
          <span>确认密码</span>
          <input v-model="confirmPassword" type="password" placeholder="请再次输入密码" />
        </label>

        <label class="form-field full-span">
          <span>性别</span>
          <select v-model="form.gender">
            <option value="">未填写</option>
            <option value="男">男</option>
            <option value="女">女</option>
          </select>
        </label>

        <p v-if="successMessage" class="form-success full-span">{{ successMessage }}</p>
        <p v-if="errorMessage" class="form-error full-span">{{ errorMessage }}</p>

        <div class="form-actions full-span">
          <button class="primary-btn" :disabled="submitting" type="submit">
            {{ submitting ? '注册中...' : '提交注册' }}
          </button>
          <RouterLink class="secondary-link" to="/login">已有账号，去登录</RouterLink>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { register } = useAuth()

const form = reactive({
  student_no: '',
  user_name: '',
  email: '',
  phone: '',
  password: '',
  gender: '',
})

const confirmPassword = ref('')
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

async function handleRegister() {
  errorMessage.value = ''
  successMessage.value = ''

  if (form.password !== confirmPassword.value) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  submitting.value = true

  try {
    await register(form)
    successMessage.value = '注册成功，请使用刚才的账号登录'
    setTimeout(() => {
      router.push('/login')
    }, 800)
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>
