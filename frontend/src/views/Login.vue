<template>
  <div class="login-container">
    <!-- Animated Background -->
    <div class="bg-animation">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <div class="login-content">
      <div class="brand-section">
        <h1 class="brand-title">Data System</h1>
        <p class="brand-subtitle">企业业务流程全生命周期管理</p>
      </div>

      <div class="login-card glass-effect">
        <h2 class="form-title">欢迎登录</h2>
        
        <el-form :model="form" class="login-form" size="large">
          <el-form-item>
            <el-input 
              v-model="form.username" 
              placeholder="用户名" 
              prefix-icon="User" 
              class="custom-input"
            />
          </el-form-item>
          <el-form-item>
            <el-input 
              v-model="form.password" 
              type="password" 
              placeholder="密码" 
              prefix-icon="Lock" 
              class="custom-input"
              show-password
            />
          </el-form-item>
          
          <el-button type="primary" class="login-btn glow-effect" @click="handleLogin" :loading="loading">
            立即登录
          </el-button>
          
          <div class="form-footer">
            <el-button link class="footer-link" @click="handleRegister">注册新账号</el-button>
            <el-divider direction="vertical" />
            <el-button link class="footer-link">忘记密码?</el-button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const form = ref({ username: '', password: '' })
const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const formData = new FormData()
    formData.append('username', form.value.username)
    formData.append('password', form.value.password)
    
    const res = await axios.post('/api/token', formData)
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('role', res.data.role)
    localStorage.setItem('username', form.value.username)
    
    ElMessage.success('登录成功，正在跳转...')
    setTimeout(() => {
      router.push('/dashboard')
    }, 800)
  } catch (error) {
    ElMessage.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请先输入用户名和密码用于注册')
    return
  }
  try {
    await axios.post('/api/register', {
      username: form.value.username,
      password: form.value.password,
      role: 'operator'
    })
    ElMessage.success('注册成功！请直接点击登录。')
  } catch (err) {
    ElMessage.error('注册失败，用户名可能已存在')
  }
}
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #0F172A;
  position: relative;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
}

/* Background Animation */
.bg-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.shape {
  position: absolute;
  filter: blur(80px);
  border-radius: 50%;
  opacity: 0.6;
  animation: float 20s infinite alternate;
}

.shape-1 {
  width: 500px;
  height: 500px;
  background: #0052FF;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 400px;
  height: 400px;
  background: #7C3AED; /* Purple */
  bottom: -50px;
  right: -50px;
  animation-delay: -5s;
}

.shape-3 {
  width: 300px;
  height: 300px;
  background: #06B6D4; /* Cyan */
  top: 40%;
  left: 40%;
  animation-delay: -10s;
  opacity: 0.4;
}

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(30px, 50px) scale(1.1); }
}

/* Content Layout */
.login-content {
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}

.brand-section {
  text-align: center;
  color: white;
}

.brand-title {
  font-family: 'Nunito', sans-serif;
  font-weight: 800;
  font-size: 3rem;
  margin: 0;
  background: linear-gradient(to right, #fff, #93C5FD);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -1px;
}

.brand-subtitle {
  color: #94A3B8;
  font-size: 1.1rem;
  margin-top: 8px;
  letter-spacing: 2px;
}

/* Glassmorphism Card */
.glass-effect {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.login-card {
  width: 380px;
  padding: 48px 40px;
  border-radius: 24px;
}

.form-title {
  color: white;
  text-align: center;
  font-weight: 500;
  margin-bottom: 32px;
  font-size: 1.5rem;
}

/* Form Styles */
:deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: none !important;
  border-radius: 12px;
  padding: 4px 12px;
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover),
:deep(.el-input__wrapper.is-focus) {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: #0052FF;
}

:deep(.el-input__inner) {
  color: white;
  height: 40px;
}

.login-btn {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  margin-top: 12px;
  background: linear-gradient(135deg, #0052FF 0%, #2563EB 100%);
  border: none;
  letter-spacing: 1px;
}

.glow-effect:hover {
  box-shadow: 0 0 20px rgba(37, 99, 235, 0.5);
  transform: translateY(-1px);
}

.form-footer {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.footer-link {
  color: #94A3B8;
  font-weight: 400;
}

.footer-link:hover {
  color: #fff;
}
</style>
