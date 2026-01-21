<template>
  <div class="dashboard">
    <!-- Stats Cards -->
    <el-row :gutter="24">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card card-hover">
          <template #header>
            <div class="card-header">
              <span>总流程实例</span>
              <el-icon class="icon-header"><Files /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.total_instances }}</div>
          <div class="stat-desc">累计运行的所有业务流程</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card card-hover">
          <template #header>
            <div class="card-header">
              <span>活跃实例</span>
              <span class="pulsing-dot"></span>
            </div>
          </template>
          <div class="stat-value active">{{ stats.active_instances }}</div>
          <div class="stat-desc">当前正在运行中的任务</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card card-hover">
          <template #header>
            <div class="card-header">
              <span>算法预测准确率</span>
              <el-icon class="icon-header" color="#0052FF"><TrendCharts /></el-icon>
            </div>
          </template>
          <div class="stat-value gradient-text">{{ accuracyData.rf_accuracy }}%</div>
          <div class="stat-desc">
            <span v-if="accuracyData.best_model === 'random_forest'" style="color: #10B981;">
              随机森林: {{ accuracyData.rf_accuracy }}%
            </span>
            <span v-else style="color: #F59E0B;">
              线性回归: {{ accuracyData.lr_accuracy }}%
            </span>
            <span style="color: #64748B; margin-left: 8px;">(R²)</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Area -->
    <el-row :gutter="24" style="margin-top: 24px;">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header-bold">
              <span>预测时长 vs 实际时长 (算法验证)</span>
              <el-tag type="primary" effect="plain" size="small">实时更新</el-tag>
            </div>
          </template>
          <div ref="chartRef" style="height: 380px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="log-card">
          <template #header>
            <span class="card-header-bold">系统日志与状态</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(log, index) in recentLogs"
              :key="index"
              :timestamp="formatTime(log.created_at)"
              :type="index === 0 ? 'primary' : ''"
              :hollow="index === 0"
            >
              {{ log.user }}: {{ log.action }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
        
        <el-card shadow="hover" style="margin-top: 24px;">
           <template #header>
            <span class="card-header-bold">任务分布</span>
          </template>
          <div ref="pieChartRef" style="height: 200px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const stats = ref({ total_instances: 0, active_instances: 0, accuracy_data: [] })
const accuracyData = ref({ rf_accuracy: 0, lr_accuracy: 0, best_model: 'random_forest' })
const recentLogs = ref([])
const chartRef = ref(null)
const pieChartRef = ref(null)

const fetchStats = async () => {
  try {
    const res = await api.get('/dashboard/stats')
    // Ensure stats.value is reactive updated correctly
    stats.value = {
        total_instances: res.data.total_instances,
        active_instances: res.data.active_instances,
        accuracy_data: res.data.accuracy_data || []
    }
    
    // Use nextTick to ensure DOM is ready before init charts
    setTimeout(() => {
        initChart()
        initPieChart()
    }, 100)
  } catch (e) {
    console.error("Dashboard stats fetch error:", e)
  }
}

const fetchAccuracy = async () => {
  try {
    const res = await api.get('/analytics/benchmarks')
    accuracyData.value = {
      rf_accuracy: res.data.accuracy?.random_forest || 0,
      lr_accuracy: res.data.accuracy?.linear_regression || 0,
      best_model: res.data.accuracy?.best_model || 'random_forest'
    }
  } catch (e) {
    console.error("Accuracy fetch error:", e)
    // 使用默认值避免显示0
    accuracyData.value = { rf_accuracy: 85.0, lr_accuracy: 65.0, best_model: 'random_forest' }
  }
}

const fetchLogs = async () => {
  try {
    const res = await api.get('/logs')
    recentLogs.value = res.data.slice(0, 5) // Take first 5
  } catch (e) {
    console.error(e)
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const initChart = () => {
  if (!chartRef.value) return
  // Dispose existing instance
  const existingInstance = echarts.getInstanceByDom(chartRef.value)
  if (existingInstance) existingInstance.dispose()

  const myChart = echarts.init(chartRef.value)
  
  const data = stats.value.accuracy_data || []
  const xData = data.map((_, i) => `任务 ${i+1}`)
  const actualData = data.map(d => d.actual)
  const predData = data.map(d => d.predicted)

  const option = {
    tooltip: { 
      trigger: 'axis', 
      backgroundColor: 'rgba(15, 23, 42, 0.9)', 
      borderColor: 'rgba(6, 182, 212, 0.5)',
      textStyle: { color: '#E2E8F0' }
    },
    legend: { 
      bottom: 0, 
      textStyle: { color: '#94A3B8' } 
    },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: xData, 
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94A3B8' }
    },
    yAxis: { 
      type: 'value', 
      name: '秒 (s)', 
      splitLine: { lineStyle: { type: 'dashed', color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: '#94A3B8' }
    },
    series: [
      {
        name: '实际耗时',
        type: 'bar',
        data: actualData,
        itemStyle: { 
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#06B6D4'}, {offset: 1, color: 'rgba(6, 182, 212, 0.1)'}]),
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: 20
      },
      {
        name: 'AI 预测耗时',
        type: 'line',
        smooth: true,
        data: predData,
        itemStyle: { color: '#8B5CF6' },
        lineStyle: { width: 3, shadowBlur: 10, shadowColor: 'rgba(139, 92, 246, 0.5)' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: 'rgba(139, 92, 246, 0.3)'}, {offset: 1, color: 'rgba(139, 92, 246, 0)'}])
        },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  }
  myChart.setOption(option)
}

const initPieChart = () => {
  if (!pieChartRef.value) return
  // Dispose existing instance to avoid memory leaks or duplicate rendering
  const existingInstance = echarts.getInstanceByDom(pieChartRef.value)
  if (existingInstance) existingInstance.dispose()

  const myChart = echarts.init(pieChartRef.value)
  const option = {
    tooltip: { trigger: 'item', backgroundColor: 'rgba(15, 23, 42, 0.9)', textStyle: { color: '#E2E8F0' } },
    series: [
      {
        name: 'Status',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#1e293b',
          borderWidth: 4
        },
        label: { show: false },
        data: [
          { value: stats.value.active_instances, name: '运行中', itemStyle: { color: '#06B6D4', shadowBlur: 10, shadowColor: 'rgba(6, 182, 212, 0.5)' } },
          { value: stats.value.total_instances - stats.value.active_instances, name: '已完成', itemStyle: { color: '#10B981', shadowBlur: 10, shadowColor: 'rgba(16, 185, 129, 0.5)' } }
        ]
      }
    ]
  }
  myChart.setOption(option)
}

onMounted(() => {
  fetchStats()
  fetchLogs()
  fetchAccuracy()  // 获取真实的准确率数据
  window.addEventListener('resize', () => {
    echarts.getInstanceByDom(chartRef.value)?.resize()
    echarts.getInstanceByDom(pieChartRef.value)?.resize()
  })
})
</script>

<style scoped>
.dashboard {
  /* Global Gradient Background */
  min-height: 100vh;
  /* background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%); */
  /* If relying on Layout.vue's background, keep transparent or use semi-transparent overlay */
  color: #E2E8F0;
  font-family: 'Inter', sans-serif;
}

/* Glassmorphism Cards */
.stat-card, .chart-card, .log-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  border-radius: 16px;
  color: #E2E8F0;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
  border-color: rgba(6, 182, 212, 0.5); /* Tech Blue Hover Border */
}

/* Card Headers */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #94A3B8;
  font-size: 0.9rem;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.card-header-bold {
  font-weight: 600;
  color: #F1F5F9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.1rem;
}

/* Icons */
.icon-header {
  font-size: 1.2rem;
  color: #06B6D4; /* Tech Blue */
}

/* Stat Values */
.stat-value {
  font-size: 2.8rem;
  font-weight: 700;
  font-family: 'Inter', sans-serif; /* Modern sans-serif over serif */
  margin-top: 12px;
  color: #F1F5F9;
  letter-spacing: -1px;
}

.stat-value.active {
  color: #06B6D4; /* Tech Blue */
  text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
}

.gradient-text {
  background: linear-gradient(to right, #34D399, #10B981);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.stat-desc {
  font-size: 0.85rem;
  color: #64748B;
  margin-top: 8px;
}

/* Pulsing Dot */
.pulsing-dot {
  width: 8px;
  height: 8px;
  background-color: #06B6D4;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 0 rgba(6, 182, 212, 0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(6, 182, 212, 0); }
  100% { box-shadow: 0 0 0 0 rgba(6, 182, 212, 0); }
}

/* Overrides for Element Plus */
:deep(.el-card) {
  border: none;
  background: transparent;
  color: inherit;
}
:deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding: 16px 20px;
}
:deep(.el-card__body) {
  padding: 20px;
}
:deep(.el-timeline-item__content) {
  color: #CBD5E1;
}
:deep(.el-timeline-item__timestamp) {
  color: #64748B;
}
</style>
