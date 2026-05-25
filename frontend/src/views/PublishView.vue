<template>
  <section class="page">
    <div class="panel">
      <h2>发布中心</h2>
      <p>这里用于展示商品发布表单、图片上传区和审核状态提示，当前仅保留前端结构。</p>
    </div>

    <div class="placeholder-card">
      <h3>商品发布表单</h3>
      <div class="form-grid">
        <label class="form-field">
          <span>商品标题</span>
          <input type="text" placeholder="例如：高数教材九成新" />
        </label>
        <label class="form-field">
          <span>商品分类</span>
          <select>
            <option>教材资料</option>
            <option>数码产品</option>
            <option>生活用品</option>
          </select>
        </label>
        <label class="form-field">
          <span>出售价格</span>
          <input type="text" placeholder="例如：35" />
        </label>
        <label class="form-field">
          <span>交易地点</span>
          <input type="text" placeholder="例如：一食堂门口" />
        </label>
        <label class="form-field" style="grid-column: 1 / -1;">
          <span>商品描述</span>
          <textarea rows="5" placeholder="描述商品成色、用途和交易说明"></textarea>
        </label>
      </div>
      <div class="form-actions">
        <button class="primary-btn">提交审核</button>
        <button class="secondary-btn">保存草稿</button>
      </div>
    </div>
  </section>
</template>
