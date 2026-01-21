<template>
  <div class="task-list">
    <el-card class="box-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>当前任务与执行状态</span>
          <el-button link type="primary" icon="Refresh" @click="fetchInstances">刷新数据</el-button>
        </div>
      </template>
      
      <el-table :data="instances" style="width: 100%" v-loading="loading" :expand-row-keys="expandedRows" row-key="id" @expand-change="handleExpand">
        <el-table-column type="expand">
          <template #default="props">
            <div class="timeline-container">
              <h4 style="margin-bottom: 20px;">流程执行时间轴</h4>
              <el-steps :active="getCurrentStepIndex(props.row)" finish-status="success" align-center>
                <el-step 
                  v-for="(node, index) in getNodes(props.row)" 
                  :key="index" 
                  :title="node.id" 
                  :description="getStepDescription(props.row, node.id)"
                />
              </el-steps>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="id" label="实例ID" width="100" align="center" />
        <el-table-column prop="current_node_id" label="当前步骤">
           <template #default="scope">
            <el-tag v-if="scope.row.status === 'Running'" effect="dark">{{ scope.row.current_node_id }}</el-tag>
            <span v-else>-</span>
           </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" effect="plain">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="AI 预测耗时 (当前步骤)" width="200">
          <template #default="scope">
            <div v-if="scope.row.status === 'Running'" class="prediction-box">
              <el-icon color="#E6A23C"><Timer /></el-icon>
              <span class="pred-value">{{ getLatestPrediction(scope.row) }} 秒</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="right">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'Running'"
              type="primary" 
              size="small" 
              @click="completeTask(scope.row.id)"
            >
              完成任务
            </el-button>
            <el-button v-else size="small" disabled>已结束</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'

const instances = ref([])
const templatesMap = ref({}) // Cache templates to show nodes
const loading = ref(false)
const expandedRows = ref([])

const fetchInstances = async () => {
  loading.value = true
  try {
    // Parallel fetch instances and templates for metadata
    const [instRes, tempRes] = await Promise.all([
      api.get('/instances'),
      api.get('/templates')
    ])
    instances.value = instRes.data
    // Create a map for quick template lookup
    templatesMap.value = tempRes.data.reduce((acc, curr) => {
      acc[curr.id] = curr
      return acc
    }, {})
  } catch (e) {
    ElMessage.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const map = { 'Running': 'primary', 'Completed': 'success', 'Terminated': 'danger' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { 'Running': '进行中', 'Completed': '已完成', 'Terminated': '已终止' }
  return map[status] || status
}

const getLatestPrediction = (row) => {
  // Simplification: In a real app we would join this data properly.
  // For now, we assume if it's running, we can check a known property or default
  // Ideally, the backend should return `current_execution` object nested.
  // We'll rely on what we have or mock it for UI demonstration if backend data is missing.
  return row.executions?.find(e => e.status === 'Running')?.predicted_duration || '计算中...'
}

const getNodes = (row) => {
  const template = templatesMap.value[row.template_id]
  return template?.graph_json?.nodes || []
}

const getCurrentStepIndex = (row) => {
  if (row.status === 'Completed') return 999
  const nodes = getNodes(row)
  return nodes.findIndex(n => n.id === row.current_node_id)
}

const getStepDescription = (row, nodeId) => {
  if (row.current_node_id === nodeId && row.status === 'Running') return '进行中'
  // Check if completed in history
  // Simplified logic
  return ''
}

const completeTask = async (id) => {
  try {
    await api.post(`/instances/${id}/complete_node`)
    ElMessage.success('任务已完成，进入下一阶段')
    fetchInstances()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const handleExpand = (row, expanded) => {
  // Logic to handle single expand if needed
}

onMounted(fetchInstances)
</script>

<style scoped>
.box-card {
  border-radius: 16px;
  border: 1px solid #E2E8F0;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
.prediction-box {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #FEF3C7;
  padding: 4px 12px;
  border-radius: 20px;
  width: fit-content;
}
.pred-value {
  color: #D97706;
  font-weight: 600;
  font-size: 0.9rem;
}
.timeline-container {
  padding: 20px 40px;
  background-color: #F8FAFC;
  border-radius: 8px;
}
</style>
