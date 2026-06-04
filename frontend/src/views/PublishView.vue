<template>
  <section class="page">
    <div class="panel">
      <h2>发布中心</h2>
      <p class="muted-text">支持商品发布、编辑、下架、重新上架、分类管理和图片展示。</p>
    </div>

    <div class="grid-2">
      <article class="section-card">
        <div class="table-header">
          <h3>{{ editingProductId ? '编辑商品' : '发布商品' }}</h3>
          <button v-if="editingProductId" class="secondary-btn" type="button" @click="resetProductForm">取消编辑</button>
        </div>
        <div class="form-grid">
          <label class="form-field">
            <span>商品标题</span>
            <input v-model.trim="productForm.title" type="text" placeholder="例如：高数教材九成新" />
          </label>
          <label class="form-field">
            <span>商品分类</span>
            <select v-model="productForm.category_name">
              <option value="">请选择分类</option>
              <option v-for="category in activeCategories" :key="category.category_id" :value="category.category_name">
                {{ category.category_name }}
              </option>
            </select>
          </label>
          <label class="form-field">
            <span>出售价格</span>
            <input v-model="productForm.price" min="0" step="0.01" type="number" placeholder="例如：35" />
          </label>
          <label class="form-field">
            <span>交易地点</span>
            <input v-model.trim="productForm.trade_location" type="text" placeholder="例如：一食堂门口" />
          </label>
          <label class="form-field full-span">
            <span>商品描述</span>
            <textarea v-model.trim="productForm.description" rows="4" placeholder="描述商品成色、用途和交易说明"></textarea>
          </label>
          <label class="form-field full-span">
            <span>图片链接</span>
            <textarea
              v-model="imageUrlText"
              rows="3"
              placeholder="每行一个图片 URL，最多 6 张"
            ></textarea>
          </label>
        </div>
        <div class="image-preview-list">
          <img v-for="url in imageUrls" :key="url" class="product-thumb large-thumb" :src="url" alt="商品图片预览" />
        </div>
        <div class="form-actions">
          <button class="primary-btn" :disabled="submittingProduct" type="button" @click="submitProduct">
            {{ submittingProduct ? '保存中...' : editingProductId ? '保存修改' : '发布商品' }}
          </button>
        </div>
        <p v-if="productMessage" class="form-success">{{ productMessage }}</p>
        <p v-if="productError" class="form-error">{{ productError }}</p>
      </article>

      <article class="section-card">
        <h3>分类管理</h3>
        <div class="form-grid">
          <label class="form-field">
            <span>分类名称</span>
            <input v-model.trim="categoryForm.category_name" type="text" placeholder="例如：运动户外" />
          </label>
          <label class="form-field">
            <span>排序值</span>
            <input v-model="categoryForm.sort_order" min="0" type="number" />
          </label>
          <label class="form-field full-span">
            <span>分类说明</span>
            <input v-model.trim="categoryForm.description" type="text" placeholder="简要说明分类用途" />
          </label>
          <label class="form-field">
            <span>状态</span>
            <select v-model="categoryForm.status">
              <option value="ACTIVE">启用</option>
              <option value="DISABLED">停用</option>
            </select>
          </label>
        </div>
        <div class="form-actions">
          <button class="primary-btn" :disabled="submittingCategory" type="button" @click="submitCategory">
            {{ submittingCategory ? '保存中...' : editingCategoryId ? '保存分类' : '新增分类' }}
          </button>
          <button v-if="editingCategoryId" class="secondary-btn" type="button" @click="resetCategoryForm">取消编辑</button>
        </div>
        <div class="category-list">
          <button
            v-for="category in categories"
            :key="category.category_id"
            class="category-chip"
            type="button"
            @click="editCategory(category)"
          >
            {{ category.category_name }}
            <span>{{ category.status === 'ACTIVE' ? '启用' : '停用' }}</span>
          </button>
        </div>
        <p v-if="categoryMessage" class="form-success">{{ categoryMessage }}</p>
        <p v-if="categoryError" class="form-error">{{ categoryError }}</p>
      </article>
    </div>

    <div class="table-card">
      <div class="table-header">
        <h3>我发布的商品</h3>
        <button class="secondary-btn" :disabled="loadingProducts" type="button" @click="loadMyProducts">
          {{ loadingProducts ? '刷新中...' : '刷新' }}
        </button>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>图片</th>
            <th>商品</th>
            <th>分类</th>
            <th>价格</th>
            <th>状态</th>
            <th>更新时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in myProducts" :key="product.product_id">
            <td><img class="product-thumb" :src="coverImage(product)" :alt="product.title" /></td>
            <td>
              <strong>{{ product.title }}</strong>
              <p class="table-subtitle">{{ product.trade_location }}</p>
            </td>
            <td>{{ product.category_name }}</td>
            <td>{{ formatPrice(product.price) }}</td>
            <td><span class="tag">{{ formatProductStatus(product.status) }}</span></td>
            <td>{{ formatDate(product.update_time) }}</td>
            <td>
              <div class="actions-cell">
                <button class="secondary-btn" :disabled="!canEdit(product)" type="button" @click="editProduct(product)">
                  编辑
                </button>
                <button
                  v-if="product.status !== 'OFFLINE'"
                  class="secondary-btn"
                  :disabled="!canOffline(product)"
                  type="button"
                  @click="handleOffline(product)"
                >
                  下架
                </button>
                <button v-else class="primary-btn" type="button" @click="handleRelist(product)">上架</button>
              </div>
            </td>
          </tr>
          <tr v-if="!myProducts.length && !loadingProducts">
            <td colspan="7" class="muted-text">暂未发布商品</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import {
  createCategory,
  createProduct,
  fetchCategories,
  fetchMyProducts,
  offlineProduct,
  relistProduct,
  updateCategory,
  updateProduct,
} from '../api/products'

const emptyProductForm = {
  title: '',
  description: '',
  price: '',
  category_name: '',
  trade_location: '',
}

const emptyCategoryForm = {
  category_name: '',
  description: '',
  sort_order: 0,
  status: 'ACTIVE',
}

const productForm = reactive({ ...emptyProductForm })
const categoryForm = reactive({ ...emptyCategoryForm })
const imageUrlText = ref('')
const editingProductId = ref(null)
const editingCategoryId = ref(null)
const submittingProduct = ref(false)
const submittingCategory = ref(false)
const loadingProducts = ref(false)
const productMessage = ref('')
const productError = ref('')
const categoryMessage = ref('')
const categoryError = ref('')
const myProducts = ref([])
const categories = ref([])

const imageUrls = computed(() =>
  imageUrlText.value
    .split('\n')
    .map((url) => url.trim())
    .filter(Boolean)
    .slice(0, 6),
)

const activeCategories = computed(() => categories.value.filter((category) => category.status === 'ACTIVE'))

function formatProductStatus(status) {
  return (
    {
      ON_SALE: '在售',
      LOCKED: '已锁定',
      SOLD: '已售出',
      OFFLINE: '已下架',
    }[status] || status
  )
}

function formatPrice(price) {
  return `${Number(price).toFixed(2)} 元`
}

function formatDate(value) {
  return new Date(value).toLocaleString()
}

function coverImage(product) {
  return product.image_urls?.[0] || 'https://dummyimage.com/120x90/e2e8f0/475569&text=SecondHand'
}

function canEdit(product) {
  return ['ON_SALE', 'OFFLINE'].includes(product.status)
}

function canOffline(product) {
  return product.status === 'ON_SALE'
}

function buildProductPayload() {
  return {
    ...productForm,
    price: String(productForm.price),
    image_urls: imageUrls.value,
  }
}

async function loadCategories() {
  categoryError.value = ''
  try {
    categories.value = await fetchCategories({ include_disabled: true })
  } catch (error) {
    categoryError.value = error.response?.data?.detail || '获取分类列表失败'
  }
}

async function loadMyProducts() {
  loadingProducts.value = true
  productError.value = ''
  try {
    myProducts.value = await fetchMyProducts()
  } catch (error) {
    productError.value = error.response?.data?.detail || '获取我发布的商品失败'
  } finally {
    loadingProducts.value = false
  }
}

async function submitProduct() {
  submittingProduct.value = true
  productMessage.value = ''
  productError.value = ''
  try {
    if (editingProductId.value) {
      await updateProduct(editingProductId.value, buildProductPayload())
      productMessage.value = '商品信息已更新'
    } else {
      await createProduct(buildProductPayload())
      productMessage.value = '商品发布成功'
    }
    resetProductForm()
    await Promise.all([loadCategories(), loadMyProducts()])
  } catch (error) {
    productError.value = error.response?.data?.detail || '保存商品失败，请检查表单内容'
  } finally {
    submittingProduct.value = false
  }
}

function editProduct(product) {
  editingProductId.value = product.product_id
  Object.assign(productForm, {
    title: product.title,
    description: product.description || '',
    price: product.price,
    category_name: product.category_name,
    trade_location: product.trade_location,
  })
  imageUrlText.value = product.image_urls?.join('\n') || ''
}

function resetProductForm() {
  editingProductId.value = null
  Object.assign(productForm, emptyProductForm)
  imageUrlText.value = ''
}

async function handleOffline(product) {
  productMessage.value = ''
  productError.value = ''
  try {
    await offlineProduct(product.product_id)
    productMessage.value = `商品“${product.title}”已下架`
    await loadMyProducts()
  } catch (error) {
    productError.value = error.response?.data?.detail || '商品下架失败'
  }
}

async function handleRelist(product) {
  productMessage.value = ''
  productError.value = ''
  try {
    await relistProduct(product.product_id)
    productMessage.value = `商品“${product.title}”已重新上架`
    await loadMyProducts()
  } catch (error) {
    productError.value = error.response?.data?.detail || '商品上架失败'
  }
}

async function submitCategory() {
  submittingCategory.value = true
  categoryMessage.value = ''
  categoryError.value = ''
  try {
    const payload = { ...categoryForm, sort_order: Number(categoryForm.sort_order) || 0 }
    if (editingCategoryId.value) {
      await updateCategory(editingCategoryId.value, payload)
      categoryMessage.value = '分类信息已更新'
    } else {
      await createCategory(payload)
      categoryMessage.value = '分类创建成功'
    }
    resetCategoryForm()
    await loadCategories()
  } catch (error) {
    categoryError.value = error.response?.data?.detail || '保存分类失败'
  } finally {
    submittingCategory.value = false
  }
}

function editCategory(category) {
  editingCategoryId.value = category.category_id
  Object.assign(categoryForm, {
    category_name: category.category_name,
    description: category.description || '',
    sort_order: category.sort_order,
    status: category.status,
  })
}

function resetCategoryForm() {
  editingCategoryId.value = null
  Object.assign(categoryForm, emptyCategoryForm)
}

onMounted(async () => {
  await Promise.all([loadCategories(), loadMyProducts()])
})
</script>
