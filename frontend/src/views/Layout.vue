<template>
  <div class="layout-container">
    <!-- Global Background Animation (Shared with Login) -->
    <div class="bg-animation">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <el-container style="height: 100vh; position: relative; z-index: 10;">
      <el-aside width="260px" class="sidebar glass-sidebar">
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-8 h-8">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="white"/>
              <path d="M2 17L12 22L22 17" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="logo-text">Data System</span>
        </div>
        
        <el-menu
          router
          :default-active="$route.path"
          class="el-menu-vertical"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataBoard /></el-icon>
            <span>总览 (Dashboard)</span>
          </el-menu-item>
          <el-menu-item index="/analytics">
            <el-icon><TrendCharts /></el-icon>
            <span>预测分析 (Analytics)</span>
          </el-menu-item>
          <el-menu-item index="/templates">
            <el-icon><Grid /></el-icon>
            <span>流程模版</span>
          </el-menu-item>
          <el-menu-item index="/tasks">
            <el-icon><Timer /></el-icon>
            <span>活跃实例</span>
          </el-menu-item>
           <el-menu-item index="/users">
            <el-icon><User /></el-icon>
            <span>资源管理</span>
          </el-menu-item>
          <el-menu-item index="/logs">
            <el-icon><Document /></el-icon>
            <span>系统日志</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header class="header glass-header">
          <div class="header-content">
            <h2 class="page-title">{{ pageTitle }}</h2>
            <div class="header-right">
              <el-icon class="header-icon" @click="showHelp"><QuestionFilled /></el-icon>
              <el-badge is-dot class="item">
                <el-icon class="header-icon" @click="showNotifications"><Bell /></el-icon>
              </el-badge>
              
              <el-dropdown>
                <span class="el-dropdown-link user-profile">
                  <el-avatar :size="36" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                  <span class="username">{{ username }}</span>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item>{{ username }}</el-dropdown-item>
                    <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>
        
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElNotification } from 'element-plus'

const route = useRoute()
const router = useRouter()
const username = ref(localStorage.getItem('username') || 'User')

const pageTitle = computed(() => {
  const map = {
    'dashboard': '系统总览',
    'analytics': '智能预测与分析',
    'templates': '流程模版管理',
    'tasks': '任务执行中心',
    'users': '资源与权限',
    'logs': '系统审计日志'
  }
  return map[route.name] || 'Data System'
})

const logout = () => {
  localStorage.clear()
  router.push('/login')
}

const showHelp = () => {
  ElMessageBox.alert(
    '欢迎使用业务流程数据管理系统。您可以：<br/>1. 在 <b>流程模版</b> 中定义业务流程。<br/>2. 在 <b>活跃实例</b> 中跟踪和执行任务。<br/>3. 在 <b>预测分析</b> 中查看 AI 耗时预测。',
    '系统帮助',
    {
      confirmButtonText: '知道了',
      dangerouslyUseHTMLString: true,
      customClass: 'glass-message-box'
    }
  )
}

const showNotifications = () => {
  ElNotification({
    title: '系统通知',
    message: '暂无新的未读消息。系统运行正常。',
    type: 'info',
    position: 'bottom-right',
    duration: 3000
  })
}
</script>

<style scoped lang="scss">
/* Reuse Background Animation */
.bg-animation {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  background-color: #0F172A;
  pointer-events: none;
}

.shape {
  position: absolute;
  filter: blur(100px);
  border-radius: 50%;
  opacity: 0.4;
  animation: float 20s infinite alternate;
}

.shape-1 { width: 600px; height: 600px; background: #0052FF; top: -200px; left: -200px; }
.shape-2 { width: 500px; height: 500px; background: #7C3AED; bottom: -100px; right: -100px; animation-delay: -5s; }
.shape-3 { width: 400px; height: 400px; background: #06B6D4; top: 30%; left: 40%; animation-delay: -10s; opacity: 0.2; }

@keyframes float {
  0% { transform: translate(0, 0); }
  100% { transform: translate(20px, 40px); }
}

/* Glass Styles */
.glass-sidebar {
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.glass-header {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  z-index: 20;
}

.sidebar {
  display: flex;
  flex-direction: column;
}

.logo {
  height: 80px;
  display: flex;
  align-items: center;
  padding-left: 24px;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #0052FF, #2563EB);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 15px rgba(0, 82, 255, 0.4);
}

.logo-icon svg { width: 24px; height: 24px; }

.logo-text {
  font-family: 'Nunito', sans-serif;
  font-weight: 800;
  font-size: 1.4rem;
  color: #fff;
  letter-spacing: -0.5px;
}

.header {
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 40px;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 500;
  color: #fff;
  margin: 0;
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
  position: relative;
  z-index: 30;
}

.header-icon {
  font-size: 20px;
  color: #94A3B8;
  cursor: pointer;
  transition: color 0.3s;
  pointer-events: auto; /* Ensure clickable */
}
.header-icon:hover { color: #fff; }

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.username {
  color: #fff;
  font-weight: 500;
}

.main-content {
  padding: 32px 40px;
  overflow-y: auto;
}
</style>
