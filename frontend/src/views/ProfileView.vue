<template>
  <section class="page">
    <div class="panel">
      <h2>个人中心</h2>
      <p class="muted-text">查看认证状态、账号信息，并维护可编辑的个人资料。</p>
    </div>

    <div class="grid-2">
      <article class="section-card">
        <h3>账号信息</h3>
        <div class="profile-meta">
          <div class="meta-item">
            <span class="meta-label">学号</span>
            <strong>{{ authState.user?.student_no || '-' }}</strong>
          </div>
          <div class="meta-item">
            <span class="meta-label">认证状态</span>
            <span class="tag">{{ authState.user?.verify_status || '未认证' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">角色</span>
            <strong>{{ authState.user?.role || '-' }}</strong>
          </div>
          <div class="meta-item">
            <span class="meta-label">信誉分</span>
            <strong>{{ authState.user?.credit_score ?? '-' }}</strong>
          </div>
          <div class="meta-item">
            <span class="meta-label">注册时间</span>
            <strong>{{ formatDate(authState.user?.create_time) }}</strong>
          </div>
          <div class="meta-item">
            <span class="meta-label">最近登录</span>
            <strong>{{ formatDate(authState.user?.last_login_time) }}</strong>
          </div>
        </div>
      </article>

      <article class="placeholder-card">
        <h3>资料维护</h3>
        <form class="form-grid" @submit.prevent="handleUpdate">
          <label class="form-field">
            <span>姓名/昵称</span>
            <input v-model="form.user_name" type="text" placeholder="请输入姓名或昵称" />
          </label>

          <label class="form-field">
            <span>手机号</span>
            <input v-model="form.phone" type="text" placeholder="请输入手机号" />
          </label>

          <label class="form-field">
            <span>邮箱</span>
            <input v-model="form.email" type="email" placeholder="请输入邮箱" />
          </label>

          <label class="form-field">
            <span>性别</span>
            <select v-model="form.gender">
              <option value="">未填写</option>
              <option value="男">男</option>
              <option value="女">女</option>
            </select>
          </label>

          <label class="form-field full-span">
            <span>头像地址</span>
            <input v-model="form.avatar_url" type="text" placeholder="请输入头像 URL（可选）" />
          </label>

          <label class="form-field full-span">
            <span>个人简介</span>
            <textarea v-model="form.bio" rows="4" placeholder="介绍一下自己"></textarea>
          </label>

          <p v-if="successMessage" class="form-success full-span">{{ successMessage }}</p>
          <p v-if="errorMessage" class="form-error full-span">{{ errorMessage }}</p>

          <div class="form-actions full-span">
            <button class="primary-btn" :disabled="submitting" type="submit">
              {{ submitting ? '保存中...' : '保存资料' }}
            </button>
          </div>
        </form>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

import { useAuth } from '../composables/useAuth'

const { authState, fetchMe, updateProfile } = useAuth()

const form = reactive({
  user_name: '',
  phone: '',
  email: '',
  gender: '',
  avatar_url: '',
  bio: '',
})

const submitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

function syncForm() {
  form.user_name = authState.user?.user_name || ''
  form.phone = authState.user?.phone || ''
  form.email = authState.user?.email || ''
  form.gender = authState.user?.gender || ''
  form.avatar_url = authState.user?.avatar_url || ''
  form.bio = authState.user?.bio || ''
}

function formatDate(value) {
  if (!value) {
    return '-'
  }

  return new Date(value).toLocaleString('zh-CN')
}

async function handleUpdate() {
  successMessage.value = ''
  errorMessage.value = ''
  submitting.value = true

  try {
    await updateProfile(form)
    syncForm()
    successMessage.value = '个人资料更新成功'
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '保存失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  if (!authState.user) {
    await fetchMe()
  }
  syncForm()
})
</script>
