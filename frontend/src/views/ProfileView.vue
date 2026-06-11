<template>
  <section class="page">
    <div class="panel">
      <h2>个人中心</h2>
      <p class="muted-text">查看认证状态、账号信息，并维护可编辑的个人资料，同时查看您的动态消息与收藏。</p>
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

      <article class="section-card" style="margin-top: 20px; grid-column: 1 / -1; border-left: 4px solid #3b82f6;">
        <h3>站内消息提醒 (用户: {{ authState.user?.user_name || '未登录' }})</h3>
        <p class="muted-text" style="font-size: 13px; margin-bottom: 15px;">
          动态拉取自数据库的通知数据，包含买家购物意向等系统状态。
        </p>

        <div v-if="notifications.length === 0" style="color: #bbb; text-align: center; padding: 20px;">
          暂无新通知
        </div>

        <div v-else style="display: flex; flex-direction: column; gap: 10px;">
          <div
            v-for="note in notifications"
            :key="note.notification_id"
            style="background: #eff6ff; border: 1px solid #bfdbfe; padding: 12px 16px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;"
          >
            <span style="color: #1e3a8a; font-size: 14px;">{{ note.content }}</span>
            <small style="color: #60a5fa; font-size: 11px; white-space: nowrap; margin-left: 10px;">
              {{ formatDate(note.create_time) }}
            </small>
          </div>
        </div>
      </article>

      <article class="section-card" style="margin-top: 10px; grid-column: 1 / -1;">
        <h3>我的收藏夹</h3>
        <p class="muted-text" style="font-size: 13px; margin-bottom: 15px;">
          实时读取当前账号的收藏商品列表。
        </p>

        <div v-if="myFavorites.length === 0" style="color: #bbb; text-align: center; padding: 20px;">
          空空如也，快去商品大厅收藏点东西吧！
        </div>

        <div v-else style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px;">
          <div
            v-for="fav in myFavorites"
            :key="fav.favorite_id"
            style="background: #fff; border: 1px solid #f59e0b; padding: 15px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"
          >
            <h4 style="margin: 0 0 8px 0; color: #f59e0b;">{{ fav.product_title }}</h4>
            <p style="margin: 5px 0; font-size: 14px;">分类: <strong>{{ fav.category_name }}</strong></p>
            <small style="color: #999; font-size: 11px;">
              时间: {{ formatDate(fav.create_time) }}
            </small>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { fetchFavorites, fetchNotifications } from '../api/social'
import { useAuth } from '../composables/useAuth'

const { authState, fetchMe, updateProfile } = useAuth()
const route = useRoute()

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
const myFavorites = ref([])
const notifications = ref([])

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

async function loadMyPrivateFavorites() {
  if (!authState.user?.user_id) {
    myFavorites.value = []
    return
  }
  try {
    myFavorites.value = await fetchFavorites()
  } catch (error) {
    console.error('获取收藏夹失败:', error)
  }
}

async function loadMyNotifications() {
  if (!authState.user?.user_id) {
    notifications.value = []
    return
  }
  try {
    notifications.value = await fetchNotifications()
  } catch (error) {
    console.error('获取通知失败:', error)
  }
}

async function refreshAllData() {
  await loadMyPrivateFavorites()
  await loadMyNotifications()
}

async function handleUpdate() {
  submitting.value = true
  successMessage.value = ''
  errorMessage.value = ''
  try {
    await updateProfile({ ...form })
    syncForm()
    successMessage.value = '个人资料已更新'
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '更新个人资料失败'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  if (!authState.user) {
    await fetchMe()
  }
  syncForm()
  await refreshAllData()
})

watch(
  () => route.path,
  async (newPath) => {
    if (newPath === '/profile') {
      await refreshAllData()
    }
  },
  { immediate: true }
)

watch(
  () => authState.user,
  async () => {
    syncForm()
    await refreshAllData()
  },
  { deep: true }
)
</script>
