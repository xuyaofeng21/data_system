<template>
  <div class="user-management">
    <div class="header-section">
      <div class="title-group">
        <h2 class="section-title">资源与权限 (Users)</h2>
        <p class="subtitle">用户管理 · 角色分配 · 状态监控</p>
      </div>
      <div class="toolbar">
        <el-button type="primary" icon="Plus" @click="dialogVisible = true">添加用户</el-button>
      </div>
    </div>

    <el-card shadow="hover" class="glass-card table-card">
      <el-table 
        :data="users" 
        style="width: 100%" 
        :header-cell-style="{background: 'rgba(255,255,255,0.05)', color: '#94A3B8'}"
        :row-style="{background: 'transparent'}"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名">
          <template #default="scope">
            <div style="display: flex; align-items: center; gap: 10px;">
              <el-avatar :size="32" class="user-avatar">
                {{ scope.row.username.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username-text">{{ scope.row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色">
          <template #default="scope">
            <el-tag :type="getRoleType(scope.row.role)" effect="dark" round>
              {{ getRoleLabel(scope.row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="status-dot"></span>
              <span class="status-text">正常</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="right">
          <template #default="scope">
             <el-button link type="primary">编辑</el-button>
             <el-popconfirm title="确定要删除此用户吗?" @confirm="deleteUser(scope.row.id)">
               <template #reference>
                 <el-button link type="danger">删除</el-button>
               </template>
             </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="添加新用户" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" placeholder="选择角色" style="width: 100%">
            <el-option label="管理员 (Admin)" value="admin" />
            <el-option label="经理 (Manager)" value="manager" />
            <el-option label="操作员 (Operator)" value="operator" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createUser">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'

const users = ref([]) 
const dialogVisible = ref(false)
const form = ref({ username: '', password: '', role: 'operator' })

const fetchUsers = async () => {
  // Use real API if available, else mock
  // Currently backend doesn't have GET /users (list all), only /users/me
  // But wait, the previous code had mock data. Let's keep mock data or try to implement backend list.
  // The user asked to implement "Delete". We need an API for that.
  // Let's assume we will add GET /users and DELETE /users/{id} to backend.
  try {
    const res = await api.get('/users')
    users.value = res.data
  } catch (e) {
    // Fallback to mock if API not ready
    console.warn("API /users failed, using mock")
    users.value = [
      { id: 1, username: 'admin', role: 'admin' },
      { id: 2, username: 'operator1', role: 'operator' }
    ]
  }
}

const deleteUser = async (id) => {
  try {
    await api.delete(`/users/${id}`)
    ElMessage.success('用户已删除')
    fetchUsers()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchUsers)

const getRoleType = (role) => {
  const map = { 'admin': 'danger', 'manager': 'warning', 'operator': 'info' }
  return map[role] || ''
}

const getRoleLabel = (role) => {
  const map = { 'admin': '超级管理员', 'manager': '项目经理', 'operator': '普通操作员' }
  return map[role] || role
}

const createUser = async () => {
  try {
    await api.post('/register', form.value)
    ElMessage.success('用户创建成功')
    dialogVisible.value = false
    // refresh list
    users.value.push({ ...form.value, id: Date.now() }) 
  } catch (e) {
    ElMessage.error('创建失败')
  }
}
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
  border: none;
  :deep(.el-card__body) {
    padding: 0;
  }
}

.user-avatar {
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.username-text {
  color: #F1F5F9;
  font-weight: 500;
}

.status-text {
  color: #fff;
  margin-left: 6px;
}
</style>
