<template>
  <div class="dashboard-view">
    <div class="header-section">
      <div class="title-group">
        <h2 class="section-title">运营指挥中心 (Operations)</h2>
        <p class="subtitle">实时监控 · 资源调度 · 异常预警</p>
      </div>
      <div class="actions">
        <el-button type="primary" icon="Refresh" @click="refreshData">刷新数据</el-button>
      </div>
    </div>

    <!-- Top KPI Cards -->
    <el-row :gutter="20" class="kpi-row">
      <el-col :span="6" v-for="(item, index) in kpiData" :key="index">
        <el-card shadow="hover" class="kpi-card glass-card">
          <div class="kpi-content">
            <div class="kpi-icon-wrapper" :class="'icon-' + index">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
            <div class="kpi-info">
              <div class="kpi-title">{{ item.title }}</div>
              <div class="kpi-value">{{ item.value }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Middle Charts Section -->
    <el-row :gutter="20" class="charts-row">
      <!-- Left Chart: Prediction vs Actual -->
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card glass-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><TrendCharts /></el-icon> 实时耗时监控 (7天趋势)</span>
            </div>
          </template>
          <div ref="lineChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- Right Chart: Resource Load -->
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card glass-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><User /></el-icon> 资源负载实时排行</span>
            </div>
          </template>
          <div class="resource-list">
            <div v-for="(res, index) in resourceLoadData" :key="index" class="resource-item">
              <div class="rank-num">{{ index + 1 }}</div>
              <el-avatar :size="36" :src="res.avatar" class="resource-avatar" />
              <div class="resource-info">
                <div class="resource-header">
                  <span class="r-name">{{ res.name }}</span>
                  <span class="r-val">{{ res.load }}%</span>
                </div>
                <div class="resource-bar-bg">
                  <div 
                    class="resource-bar-fill" 
                    :style="{ width: res.load + '%', background: getLoadColor(res.load) }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Bottom Table Section -->
    <el-row class="table-row">
      <el-col :span="24">
        <el-card shadow="hover" class="glass-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><List /></el-icon> 最近活跃流程实例</span>
              <el-tag effect="dark" type="success" size="small">实时更新</el-tag>
            </div>
          </template>
          <el-table :data="recentInstances" style="width: 100%" :header-cell-style="{background: 'transparent'}">
            <el-table-column prop="processName" label="流程名称" min-width="180">
              <template #default="{ row }">
                <span class="process-name">{{ row.processName }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="currentNode" label="当前节点" />
            <el-table-column label="执行人">
              <template #default="scope">
                <div class="assigned-resource">
                  <el-avatar :size="24" :src="scope.row.resourceAvatar" />
                  <span class="resource-name">{{ scope.row.resourceName }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="predictedFinish" label="预计完成时间" min-width="150" />
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)" effect="dark" round size="small">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default>
                <el-button link type="primary" size="small">详情</el-button>
                <el-button link type="warning" size="small">催办</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

// --- Mock Data ---

// 1. KPI Data
const kpiData = ref([
  { title: '总流程数', value: '328', icon: 'Files' },
  { title: '活跃实例', value: '45', icon: 'Cpu' },
  { title: '今日完成', value: '12', icon: 'Check' },
  { title: '平均耗时', value: '4.2h', icon: 'Timer' }
])

// 2. Resource Load Data
const resourceLoadData = ref([
  { name: '用户 A', avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png', load: 92 },
  { name: '用户 B', avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png', load: 85 },
  { name: '用户 C', avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png', load: 60 },
  { name: '用户 D', avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png', load: 45 },
])

const getLoadColor = (load: number) => {
  if (load > 90) return 'linear-gradient(90deg, #F87171, #EF4444)'
  if (load > 70) return 'linear-gradient(90deg, #FBBF24, #F59E0B)'
  return 'linear-gradient(90deg, #60A5FA, #3B82F6)'
}

// 3. Recent Instances Data
const recentInstances = ref([
  {
    processName: '采购审批流程 A1',
    currentNode: '主管审批',
    resourceName: '张伟',
    resourceAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    predictedFinish: '4月16日 21:00',
    status: '进行中'
  },
  {
    processName: '报销流程 A2',
    currentNode: '财务复核',
    resourceName: '李娜',
    resourceAvatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
    predictedFinish: '4月13日 15:00',
    status: '等待中'
  },
  {
    processName: '入职流程 A3',
    currentNode: '人事归档',
    resourceName: '王强',
    resourceAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    predictedFinish: '4月13日 14:30',
    status: '进行中'
  },
  {
    processName: '合同评审 B1',
    currentNode: '法务审核',
    resourceName: '赵敏',
    resourceAvatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
    predictedFinish: '4月14日 10:00',
    status: '进行中'
  }
])

const getStatusType = (status: string) => {
  if (status === 'Running' || status === '进行中') return 'primary'
  if (status === 'Pending' || status === '等待中') return 'warning'
  return 'info'
}

const refreshData = () => {
  ElMessage.success('数据已更新')
}

// --- ECharts Implementation ---
const lineChartRef = ref<HTMLElement | null>(null)
let myChart: echarts.ECharts | null = null

const initChart = () => {
  if (!lineChartRef.value) return
  
  myChart = echarts.init(lineChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: '#334155',
      textStyle: { color: '#F1F5F9' }
    },
    legend: {
      data: ['预测耗时', '实际耗时'],
      bottom: 0,
      textStyle: { color: '#94A3B8' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'],
      axisLine: {
        lineStyle: { color: 'rgba(255,255,255,0.1)' }
      },
      axisLabel: {
        color: '#94A3B8'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#94A3B8' },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: 'rgba(255,255,255,0.05)'
        }
      }
    },
    series: [
      {
        name: '预测耗时',
        type: 'line',
        smooth: true,
        data: [20, 70, 50, 80, 90, 80, 130],
        lineStyle: { color: '#0052FF', width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 82, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 82, 255, 0)' }
          ])
        },
        showSymbol: false
      },
      {
        name: '实际耗时',
        type: 'line',
        smooth: true,
        data: [20, 50, 60, 80, 60, 90, 110],
        lineStyle: { color: '#7C3AED', width: 3 }, // Purple
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(124, 58, 237, 0.3)' },
            { offset: 1, color: 'rgba(124, 58, 237, 0)' }
          ])
        },
        showSymbol: false
      }
    ]
  }
  
  myChart.setOption(option)
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  myChart?.dispose()
})

const handleResize = () => {
  myChart?.resize()
}

</script>

<style scoped lang="scss">
.dashboard-view {
  /* No padding needed as Main has it */
}

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

.kpi-row {
  margin-bottom: 24px;
}

.kpi-card {
  border: none;
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  
  :deep(.el-card__body) {
    padding: 20px;
  }
}

.kpi-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  
  &.icon-0 { background: rgba(0, 82, 255, 0.1); color: #60A5FA; }
  &.icon-1 { background: rgba(16, 185, 129, 0.1); color: #34D399; }
  &.icon-2 { background: rgba(245, 158, 11, 0.1); color: #FBBF24; }
  &.icon-3 { background: rgba(124, 58, 237, 0.1); color: #A78BFA; }
}

.kpi-title {
  font-size: 14px;
  color: #94A3B8;
  margin-bottom: 4px;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  font-family: 'Inter', sans-serif;
}

.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #F1F5F9;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 10px 0;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rank-num {
  width: 20px;
  color: #64748B;
  font-weight: 600;
  text-align: center;
}

.resource-info {
  flex: 1;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
}

.r-name { color: #E2E8F0; }
.r-val { color: #94A3B8; }

.resource-bar-bg {
  height: 6px;
  width: 100%;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.resource-bar-fill {
  height: 100%;
  border-radius: 3px;
}

.process-name {
  color: #fff;
  font-weight: 500;
}

.assigned-resource {
  display: flex;
  align-items: center;
  gap: 8px;
}

.resource-name {
  color: #CBD5E1;
}
</style>
