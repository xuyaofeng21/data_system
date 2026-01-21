<template>
  <div class="templates-view">
    <div class="header-section">
      <div class="title-group">
        <h2 class="section-title">流程模版管理 (Templates)</h2>
        <p class="subtitle">业务流程定义 · 版本控制 · 快速实例化</p>
      </div>
      <div class="toolbar">
        <el-button type="primary" icon="Plus" @click="dialogVisible = true" class="create-btn">
          新建流程模型
        </el-button>
      </div>
    </div>

    <el-card shadow="hover" class="glass-card table-card">
      <el-table 
        :data="templates" 
        style="width: 100%" 
        v-loading="loading"
        :header-cell-style="{background: 'rgba(255,255,255,0.05)', color: '#94A3B8'}"
        :row-style="{background: 'transparent'}"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="流程名称">
          <template #default="scope">
            <span class="process-name">{{ scope.row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本号" width="100" align="center">
           <template #default="scope">
            <el-tag effect="dark" type="info" round size="small">v{{ scope.row.version }}.0</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="280" align="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button size="small" type="primary" plain class="glass-btn glass-btn-primary" @click="startInstance(scope.row.id)">
                启动
              </el-button>
              <el-button size="small" type="warning" plain class="glass-btn glass-btn-warning" icon="Edit" @click="openEditDialog(scope.row)">
                编辑
              </el-button>
              <el-popconfirm title="确定要删除此模版吗?" @confirm="deleteTemplate(scope.row.id)">
                <template #reference>
                  <el-button size="small" type="danger" plain class="glass-btn glass-btn-danger" icon="Delete">
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEditMode ? '编辑业务流程' : '定义新业务流程'" width="600px" destroy-on-close @closed="resetForm">
      <el-form :model="form" label-position="top">
        <el-form-item label="流程名称">
          <el-input v-model="form.name" placeholder="例如：采购审批流程" />
        </el-form-item>
        <el-form-item label="节点定义 (JSON格式)">
          <el-input 
            type="textarea" 
            v-model="form.graph_json" 
            :rows="6" 
            font-family="monospace"
            placeholder='{"nodes": [{"id": "Start"}, {"id": "Approval"}, {"id": "End"}]}' 
          />
          <div class="form-tip">
            支持的节点类型: Start, Task, Approval, End. 请确保JSON格式正确。
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="saveTemplate">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const templates = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEditMode = ref(false)
const currentId = ref(null)
const form = ref({ name: '', graph_json: '{"nodes": [{"id": "开始节点"}, {"id": "部门审批"}, {"id": "财务复核"}, {"id": "结束"}]}' })
const router = useRouter()

const fetchTemplates = async () => {
  loading.value = true
  try {
    const res = await api.get('/templates')
    templates.value = res.data
  } catch (e) {
    ElMessage.error('获取流程列表失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  isEditMode.value = false
  currentId.value = null
  form.value = { name: '', graph_json: '{"nodes": [{"id": "开始节点"}, {"id": "部门审批"}, {"id": "财务复核"}, {"id": "结束"}]}' }
}

const openEditDialog = (row) => {
  isEditMode.value = true
  currentId.value = row.id
  form.value = {
    name: row.name,
    graph_json: JSON.stringify(row.graph_json, null, 2)
  }
  dialogVisible.value = true
}

const saveTemplate = async () => {
  try {
    const payload = {
      name: form.value.name,
      graph_json: JSON.parse(form.value.graph_json)
    }
    
    if (isEditMode.value) {
      await api.put(`/templates/${currentId.value}`, payload)
      ElMessage.success('流程模型更新成功')
    } else {
      await api.post('/templates', payload)
      ElMessage.success('流程模型创建成功')
    }
    
    dialogVisible.value = false
    fetchTemplates()
  } catch (e) {
    ElMessage.error('操作失败，请检查JSON格式')
  }
}

const deleteTemplate = async (id) => {
  try {
    await api.delete(`/templates/${id}`)
    ElMessage.success('流程模型已删除')
    fetchTemplates()
  } catch (e) {
    ElMessage.error('删除失败，可能存在关联实例')
  }
}

const startInstance = async (id) => {
  try {
    await api.post('/instances', { template_id: id })
    ElMessage.success('流程实例已启动')
    router.push('/tasks')
  } catch (e) {
    console.error(e)
    const msg = e.response?.data?.detail || '启动失败'
    ElMessage.error(msg)
  }
}

onMounted(fetchTemplates)
</script>

<style scoped lang="scss">
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
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

.process-name {
  color: #fff;
  font-weight: 500;
}

.form-tip {
  font-size: 12px;
  color: #94A3B8;
  margin-top: 4px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.glass-btn {
  border-radius: 8px;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }
}

.glass-btn-primary {
  background: rgba(0, 82, 255, 0.1);
  border: 1px solid rgba(0, 82, 255, 0.3);
  color: #60A5FA;
  
  &:hover {
    background: rgba(0, 82, 255, 0.2);
    color: #fff;
    border-color: #60A5FA;
  }
}

.glass-btn-warning {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #FBBF24;
  
  &:hover {
    background: rgba(245, 158, 11, 0.2);
    color: #fff;
    border-color: #FBBF24;
  }
}

.glass-btn-danger {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #F87171;
  
  &:hover {
    background: rgba(239, 68, 68, 0.2);
    color: #fff;
    border-color: #F87171;
  }
}
</style>
