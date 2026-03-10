<template>
  <div class="content-access-alert" :class="`access-level-${accessLevel}`">
    <div class="alert-icon">
      <span v-if="accessLevel === 'full'">✓</span>
      <span v-else-if="accessLevel === 'metadata'">ℹ️</span>
      <span v-else>⚠️</span>
    </div>
    <div class="alert-content">
      <div class="alert-title">
        <template v-if="accessLevel === 'full'">
          完整访问权限
        </template>
        <template v-else-if="accessLevel === 'metadata'">
          受限访问 - 仅元数据
        </template>
        <template v-else>
          无访问权限
        </template>
      </div>
      <div class="alert-message">
        <template v-if="accessLevel === 'full'">
          您可以查看教材的完整内容，包括正文和代码示例。
        </template>
        <template v-else-if="accessLevel === 'metadata'">
          作为审核员，您只能查看教材的基本信息和元数据，无法访问正文内容。
          审核工作应基于教材的元数据、AI审核结果和教师提供的说明进行。
        </template>
        <template v-else>
          您没有权限访问此教材的内容。请联系管理员获取权限。
        </template>
      </div>
      <div v-if="accessLevel === 'metadata'" class="accessible-fields">
        <div class="fields-title">可访问字段：</div>
        <div class="fields-list">
          <span v-for="field in accessibleFields" :key="field" class="field-tag">
            {{ field }}
          </span>
        </div>
      </div>
      <div v-if="accessLevel === 'metadata'" class="restricted-fields">
        <div class="fields-title">受限字段：</div>
        <div class="fields-list">
          <span v-for="field in restrictedFields" :key="field" class="field-tag restricted">
            {{ field }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  accessLevel: {
    type: String,
    default: 'metadata', // 'full', 'metadata', 'none'
    validator: (value) => ['full', 'metadata', 'none'].includes(value)
  },
  accessibleFields: {
    type: Array,
    default: () => [
      '标题', '作者', '版本', '字数', '章节数', 
      '描述', '分类', '标签', '教师信息', '修改历史'
    ]
  },
  restrictedFields: {
    type: Array,
    default: () => [
      '正文内容', '章节详情', '代码示例', '附件文件'
    ]
  }
})
</script>

<style scoped>
.content-access-alert {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.access-level-full {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
}

.access-level-metadata {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
}

.access-level-none {
  background: #fff2f0;
  border: 1px solid #ffccc7;
}

.alert-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 8px;
}

.access-level-full .alert-title {
  color: #52c41a;
}

.access-level-metadata .alert-title {
  color: #1890ff;
}

.access-level-none .alert-title {
  color: #f5222d;
}

.alert-message {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
}

.fields-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.fields-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.field-tag {
  padding: 2px 8px;
  background: #f0f5ff;
  color: #1890ff;
  border-radius: 4px;
  font-size: 12px;
}

.field-tag.restricted {
  background: #fff2f0;
  color: #f5222d;
}

.accessible-fields {
  margin-bottom: 12px;
}
</style>
