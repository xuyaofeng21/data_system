<template>
  <div class="system-logs-view">
    <div class="header-section">
      <div class="title-group">
        <h2 class="section-title">系统审计日志 (Audit Logs)</h2>
        <p class="subtitle">用户行为追踪 · 安全审计 · 异常排查</p>
      </div>
      <div class="actions">
        <el-button type="primary" icon="Refresh" @click="fetchLogs" :loading="loading">刷新日志</el-button>
        <el-button icon="Download" class="glass-btn">导出报表</el-button>
      </div>
    </div>

    <el-card shadow="hover" class="glass-card table-card">
      <el-table 
        :data="logs" 
        style="width: 100%" 
        v-loading="loading"
        :header-cell-style="{background: 'rgba(255,255,255,0.05)', color: '#94A3B8'}"
        :row-style="{background: 'transparent'}"
      >
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            <span class="log-time">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="user_id" label="操作用户" width="120">
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar :size="24" class="user-avatar">{{ row.user_id ? row.user_id.charAt(0).toUpperCase() : 'U' }}</el-avatar>
              <span class="user-name">User {{ row.user_id }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="action" label="行为类型" width="150">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)" effect="dark" size="small" round>
              {{ row.action }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="details" label="详细信息" min-width="250">
          <template #default="{ row }">
            <span class="log-details">{{ row.details }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="ip_address" label="IP 地址" width="140">
          <template #default="{ row }">
            <span class="ip-tag">{{ row.ip_address || '127.0.0.1' }}</span>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="100"
          class="glass-pagination"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const logs = ref([])
const loading = ref(false)

const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/logs')
    logs.value = res.data
  } catch (err) {
    ElMessage.error('获取日志失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

const getActionType = (action) => {
  const map = {
    'LOGIN': 'success',
    'REGISTER': 'primary',
    'CREATE_TEMPLATE': 'warning',
    'START_INSTANCE': 'danger',
    'COMPLETE_TASK': 'info'
  }
  return map[action] || 'info'
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped lang="scss">
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-family: 'Calistoga', serif;
  font-size: 1.8rem;
  color: #fff;
  margin: 0;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.subtitle {
  color: #94A3B8;
  margin-top: 4px;
  font-size: 0.9rem;
}

.glass-card {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}

.table-card {
  :deep(.el-card__body) {
    padding: 0;
  }
}

.log-time {
  color: #CBD5E1;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: #fff;
  font-size: 12px;
}

.user-name {
  color: #E2E8F0;
  font-weight: 500;
}

.log-details {
  color: #94A3B8;
}

.ip-tag {
  color: #64748B;
  font-family: monospace;
  background: rgba(0,0,0,0.2);
  padding: 2px 6px;
  border-radius: 4px;
}

.glass-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #E2E8F0;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border-color: rgba(255, 255, 255, 0.2);
  }
}

.pagination-container {
  padding: 16px 24px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* Pagination Overrides for Dark Mode */
:deep(.el-pagination.is-background .el-pager li:not(.is-active)) {
  background-color: rgba(255, 255, 255, 0.05);
  color: #94A3B8;
}

:deep(.el-pagination.is-background .btn-prev),
:deep(.el-pagination.is-background .btn-next) {
  background-color: rgba(255, 255, 255, 0.05);
  color: #94A3B8;
}

:deep(.el-table__inner-wrapper::before) {
  display: none; /* Remove bottom border */
}
</style>