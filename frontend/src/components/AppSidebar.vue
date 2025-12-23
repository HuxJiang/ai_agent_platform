<template>
  <aside class="sidebar">
    <nav class="menu">
      <ul class="menu-list">
        <li class="menu-item">
          <router-link to="/home" class="menu-link" active-class="active">
            <span class="menu-icon">🏠</span>
            <span class="menu-text">MCP广场</span>
          </router-link>
        </li>
        <li class="menu-item">
          <router-link to="/mymcp" class="menu-link" active-class="active">
            <span class="menu-icon">🛠️</span>
            <span class="menu-text">我的MCP</span>
          </router-link>
        </li>
        <li class="menu-item">
          <router-link to="/workflow" class="menu-link" active-class="active">
            <span class="menu-icon">⇆</span>
            <span class="menu-text">工作流</span>
          </router-link>
        </li>
        <li class="menu-item">
          <router-link to="/knowledge" class="menu-link" active-class="active">
            <span class="menu-icon">📚</span>
            <span class="menu-text">知识库</span>
          </router-link>
        </li>
        <li class="menu-item">
          <router-link to="/conversation" class="menu-link" active-class="active">
            <span class="menu-icon">💬</span>
            <span class="menu-text">会话管理</span>
          </router-link>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<script>
export default {
  name: 'AppSidebar'
}
</script>

<style scoped>
.sidebar {
  width: 240px;
  background-color: #ffffff;
  border-right: 1px solid #e5e7eb;
  padding: 24px 16px;
  flex-shrink: 0;
}
.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.menu-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  text-decoration: none;
  color: #4b5563;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s;
}
.menu-link:hover {
  background-color: #f3f4f6;
  color: #111827;
}
.menu-link.active {
  background-color: #e0e7ff;
  color: #4f46e5;
  font-weight: 600;
}
</style>
