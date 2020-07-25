<template>
  <div>
    <!--相同的index会同时打开,设置router实现路由跳转，依赖index值-->
    <el-row :gutter="0">
      <el-menu
        :default-active="this.$router.path"
        class="el-menu-demo"
        router
        mode="horizontal"
        @select="handleSelect"
      >
        <el-col :span="2">
          <el-menu-item index="/">首页</el-menu-item>
        </el-col>
        <el-col :span="2">
          <el-submenu index="syz">
            <template slot="title">我的淘小宝</template>
            <el-menu-item index="2-1">已买到的甜心</el-menu-item>
          </el-submenu>
        </el-col>
        <el-col :span="2">
          <el-submenu index="syz6">
            <template slot="title">收藏夹</template>
            <el-menu-item index="3-1">收藏的甜心</el-menu-item>
            <router-view></router-view>
            <el-menu-item index="3-2">收藏的商铺</el-menu-item>
          </el-submenu>
        </el-col>
        <el-col :span="2">
          <el-submenu index="syz66">
            <template slot="title">商家通道</template>
            <el-menu-item index="4-1">开店</el-menu-item>
            <el-menu-item index="4-2">已卖出的甜心</el-menu-item>
            <el-menu-item index="4-3">出售中的甜心</el-menu-item>
            <el-menu-item index="4-4">最近消息</el-menu-item>
          </el-submenu>
        </el-col>
        <el-col :span="2">
          <el-submenu index="syz666">
            <template slot="title">商家通道</template>
            <el-menu-item index="5-1">查询订单</el-menu-item>
          </el-submenu>
        </el-col>
        <el-col :span="2">
          <el-submenu index="syz6666">
            <template slot="title">亲 看这里</template>
            <el-menu-item index="/register">注册</el-menu-item>
            <el-menu-item index="/login">登录</el-menu-item>
          </el-submenu>
        </el-col>
        <el-col :span="1" :offset="6">
          <el-menu-item index="head">
            <el-avatar src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></el-avatar>
          </el-menu-item>
        </el-col>
        <el-col :span="2" :offset="0">
          <el-menu-item index="user">用户</el-menu-item>
        </el-col>
        <el-col :span="2" offset="0">
          <el-menu-item index="user">
          <el-dropdown trigger="hover">
            <span class="el-dropdown-link">
              消息提醒
              <i class="el-icon-caret-bottom el-icon--right"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item class="clearfix">
                通知
                <el-badge class="mark" :value="12" />
              </el-dropdown-item>
              <el-dropdown-item class="clearfix">
                回复
                <el-badge class="mark" :value="3" />
              </el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
          </el-menu-item>
        </el-col>
      </el-menu>
    </el-row>
    <!--一定要有router-view,用来加载路由定向的组件-->
    <router-view />
  </div>
</template>
<script>
export default {
  name: "Header",
  data() {
    return {
      // 默认返回的index
    };
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
