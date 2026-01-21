<template>
  <div class="analytics-view">
    <div class="header-section">
      <div class="title-group">
        <h2 class="section-title">实验室: 算法模型深度分析</h2>
        <p class="subtitle">历史数据回溯 · 模型性能基准测试 · 影响因子挖掘</p>
      </div>
      
      <div class="actions">
        <el-button type="primary" :loading="training" @click="runBenchmark" icon="VideoPlay">
          运行基准测试 (Benchmark)
        </el-button>
      </div>
    </div>

    <!-- Benchmark Section -->
    <el-row :gutter="24">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>模型性能对比 (MSE 误差分布)</span>
              <div class="tag-group">
                <el-tag type="info">线性回归</el-tag>
                <el-tag type="warning">SVM</el-tag>
                <el-tag type="success" effect="dark">随机森林 (当前)</el-tag>
              </div>
            </div>
          </template>
          <div ref="benchmarkChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">核心指标概览</div>
          </template>
          
          <div class="stat-item">
            <div class="label">最优模型 (Best Model)</div>
            <div class="value highlight">{{ bestModel }}</div>
            <div class="desc">R² Score: {{ bestR2 }}</div>
          </div>
          <el-divider class="glass-divider" />
          <div class="stat-item">
            <div class="label">平均平方误差 (MSE)</div>
            <div class="value">{{ bestMSE }}</div>
            <div class="desc">误差已最小化</div>
          </div>
          <el-divider class="glass-divider" />
          <div class="stat-item">
            <div class="label">数据样本量</div>
            <div class="value">1,248</div>
            <div class="desc">已清洗有效数据</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Deep Insights -->
    <el-row :gutter="24" style="margin-top: 24px;">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>特征重要性 (Feature Importance)</span>
              <el-tooltip content="分析哪些因素最影响任务耗时" placement="top">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div ref="featureChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>预测残差分析 (Residuals)</span>
            </div>
          </template>
          <div ref="residualChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import api from '../api'

const training = ref(false)
const benchmarkChartRef = ref(null)
const featureChartRef = ref(null)
const residualChartRef = ref(null)
const metrics = ref(null)
const bestModel = ref('Loading...')
const bestR2 = ref('0.00')
const bestMSE = ref('0.00')

let charts = []

const runBenchmark = async () => {
  training.value = true
  try {
    const res = await api.get('/analytics/benchmarks')
    metrics.value = res.data
    
    // Update Stats
    const rf = metrics.value.rf
    const lr = metrics.value.lr
    
    if (rf.r2 > lr.r2) {
      bestModel.value = 'Random Forest'
      bestR2.value = rf.r2.toFixed(3)
      bestMSE.value = rf.mse.toFixed(2)
    } else {
      bestModel.value = 'Linear Regression'
      bestR2.value = lr.r2.toFixed(3)
      bestMSE.value = lr.mse.toFixed(2)
    }
    
    updateCharts()
    ElMessage.success('基准测试完成！数据已更新。')
  } catch (e) {
    ElMessage.error('测试失败')
  } finally {
    training.value = false
  }
}

const updateCharts = () => {
  if (!metrics.value || !benchmarkChartRef.value) return

  const rf = metrics.value.rf
  const lr = metrics.value.lr

  // 1. Benchmark Chart (Dual Axis: MSE vs R2)
  const chart1 = echarts.getInstanceByDom(benchmarkChartRef.value) || echarts.init(benchmarkChartRef.value)
  chart1.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { textStyle: { color: '#ccc' }, bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: ['Linear Regression', 'Random Forest'],
      axisLabel: { color: '#94A3B8' }
    },
    yAxis: [
      {
        type: 'value',
        name: 'MSE (误差)',
        nameTextStyle: { color: '#94A3B8' },
        axisLabel: { color: '#94A3B8' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
      },
      {
        type: 'value',
        name: 'R² Score (准确率)',
        nameTextStyle: { color: '#94A3B8' },
        axisLabel: { color: '#94A3B8' },
        min: 0,
        max: 1,
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'MSE (越低越好)',
        type: 'bar',
        data: [lr.mse, rf.mse],
        itemStyle: { color: '#F59E0B' },
        barWidth: 40
      },
      {
        name: 'R² Score (越高越好)',
        type: 'line',
        yAxisIndex: 1,
        data: [lr.r2, rf.r2],
        itemStyle: { color: '#10B981' },
        symbolSize: 10,
        lineStyle: { width: 3 }
      }
    ]
  })
}

const initCharts = () => {
  // Initial empty charts or placeholders
  if (benchmarkChartRef.value) {
    const chart = echarts.init(benchmarkChartRef.value)
    charts.push(chart)
  }
  if (featureChartRef.value) {
    const chart = echarts.init(featureChartRef.value)
    // Static Feature Importance (Mock for now as backend doesn't return this yet)
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'value', axisLabel: { color: '#94A3B8' }, splitLine: { show: false } },
      yAxis: { 
        type: 'category', 
        data: ['任务复杂度', '前序节点耗时', '执行人当前负载', '时间段(Hour)', '任务类型'],
        axisLabel: { color: '#fff' }
      },
      series: [{
        type: 'bar',
        data: [85, 60, 45, 25, 15],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
            { offset: 0, color: '#4D7CFF' },
            { offset: 1, color: '#0052FF' }
          ]),
          borderRadius: [0, 4, 4, 0]
        },
        barWidth: 15
      }]
    })
    charts.push(chart)
  }
  if (residualChartRef.value) {
    const chart = echarts.init(residualChartRef.value)
    // Static Mock for Residuals
    const data = Array.from({length: 50}, () => [
      Math.random() * 300, 
      (Math.random() - 0.5) * 40
    ])
    chart.setOption({
      tooltip: { formatter: 'Predicted: {c0}<br/>Error: {c1}' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { name: 'Predicted', nameTextStyle: { color: '#94A3B8' }, axisLabel: { color: '#94A3B8' } },
      yAxis: { name: 'Residual', nameTextStyle: { color: '#94A3B8' }, axisLabel: { color: '#94A3B8' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
      series: [{
        type: 'scatter',
        data: data,
        itemStyle: { color: '#F472B6' },
        symbolSize: 8
      }]
    })
    charts.push(chart)
  }
}

onMounted(() => {
  initCharts()
  runBenchmark() // Fetch real data on load
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach(c => c.dispose())
})

const handleResize = () => {
  charts.forEach(c => c.resize())
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

.chart-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #F1F5F9;
}

.tag-group {
  display: flex;
  gap: 8px;
}

.chart-container {
  height: 320px;
  width: 100%;
}

.stat-card {
  height: 100%;
}

.stat-item {
  padding: 20px 0;
  text-align: center;
}

.label {
  color: #94A3B8;
  font-size: 0.9rem;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #fff;
  font-family: 'Inter', sans-serif;
}

.value.highlight {
  background: linear-gradient(to right, #34D399, #10B981);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.desc {
  font-size: 0.85rem;
  color: #64748B;
  margin-top: 4px;
}

.glass-divider {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  margin: 0;
}
</style>
