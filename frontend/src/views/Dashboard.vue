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
          <div class="stat-value gradient-text">92%</div>
          <div class="stat-desc">基于随机森林回归模型</div>
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
            <el-timeline-item timestamp="刚刚" type="primary" hollow>
              系统数据同步完成
            </el-timeline-item>
            <el-timeline-item timestamp="10分钟前" color="#0bbd87">
              预测模型自动重训练完成 (Loss: 0.024)
            </el-timeline-item>
            <el-timeline-item timestamp="1小时前">
              管理员 admin 登录系统
            </el-timeline-item>
             <el-timeline-item timestamp="2小时前">
              新增流程模板 "采购审批 v2"
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
const chartRef = ref(null)
const pieChartRef = ref(null)

const fetchStats = async () => {
  try {
    const res = await api.get('/dashboard/stats')
    stats.value = res.data
    initChart()
    initPieChart()
  } catch (e) {
    console.error(e)
  }
}

const initChart = () => {
  if (!chartRef.value) return
  const myChart = echarts.init(chartRef.value)
  
  const data = stats.value.accuracy_data || []
  const xData = data.map((_, i) => `任务 ${i+1}`)
  const actualData = data.map(d => d.actual)
  const predData = data.map(d => d.predicted)

  const option = {
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.9)' },
    legend: { bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: xData, axisLine: { lineStyle: { color: '#CBD5E1' } } },
    yAxis: { type: 'value', name: '秒 (s)', splitLine: { lineStyle: { type: 'dashed' } } },
    series: [
      {
        name: '实际耗时',
        type: 'bar',
        data: actualData,
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#4D7CFF'}, {offset: 1, color: '#0052FF'}]) },
        barWidth: 20,
        itemStyle: { borderRadius: [4, 4, 0, 0], color: '#0052FF' }
      },
      {
        name: 'AI 预测耗时',
        type: 'line',
        data: predData,
        itemStyle: { color: '#F59E0B' },
        lineStyle: { width: 3, type: 'dashed' },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  }
  myChart.setOption(option)
}

const initPieChart = () => {
  if (!pieChartRef.value) return
  const myChart = echarts.init(pieChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    series: [
      {
        name: 'Status',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false },
        data: [
          { value: stats.value.active_instances, name: '运行中', itemStyle: { color: '#0052FF' } },
          { value: stats.value.total_instances - stats.value.active_instances, name: '已完成', itemStyle: { color: '#10B981' } }
        ]
      }
    ]
  }
  myChart.setOption(option)
}

onMounted(() => {
  fetchStats()
  window.addEventListener('resize', () => {
    echarts.getInstanceByDom(chartRef.value)?.resize()
    echarts.getInstanceByDom(pieChartRef.value)?.resize()
  })
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #64748B;
  font-size: 0.9rem;
}
.card-header-bold {
  font-weight: 600;
  color: #1E293B;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  font-family: 'Calistoga', serif;
  margin-top: 8px;
  color: #1E293B;
}
.stat-value.active {
  color: #0052FF;
}
.stat-desc {
  font-size: 0.8rem;
  color: #94A3B8;
  margin-top: 4px;
}
.pulsing-dot {
  width: 8px;
  height: 8px;
  background-color: #10B981;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 0 rgba(16, 185, 129, 0.4);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}
</style>
