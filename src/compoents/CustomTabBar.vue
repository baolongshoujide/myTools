
<template>
  <view class="custom-tabbar">
    <!-- 首页 -->
    <view class="tab-item" :class="{ 'tab-item-active': isActive('/pages/index/index') }" @click="goTab('/pages/index/index')">
      <uni-icons type="home" size="24" :color="isActive('/pages/index/index') ? '#2878ff' : '#888'" />
      <text>首页</text>
    </view>

    <!-- 功能 -->
    <view class="tab-item" :class="{ 'tab-item-active': isActive('/pages/function/index') }" @click="goTab('/pages/function/index')">
      <uni-icons type="bars" size="24" :color="isActive('/pages/function/index') ? '#2878ff' : '#888'" />
      <text>功能</text>
    </view>

    <!-- 中间加号 -->
    <view class="tab-item plus-item" @touchstart="isLong = false" @longpress="goHome">
       <view class="plus-circle">
          <uni-icons
            v-if="isLong"
            type="home"
            size="30"
            color="#fff"
          />
       <text v-else class="plus">＋</text>
       </view>
    </view>
    <!-- 列表 -->
    <view class="tab-item" :class="{ 'tab-item-active': isActive('/pages/list/index') }" @click="goTab('/pages/list/index')">
  <uni-icons
    type="list"
    size="24"
    :color="isActive('/pages/list/index') ? '#2878ff' : '#888'"
  />
  <text>列表</text>
</view>
    <view class="tab-item" :class="{ 'tab-item-active': isActive('/pages/my/index') }" @click="goTab('/pages/my/index')">
      <uni-icons type="person" size="24" :color="isActive('/pages/my/index') ? '#2878ff' : '#888'" />
      <text>我的</text>
    </view>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app';
import { onMounted, ref } from 'vue';

const currentRoute = ref('')

const updateCurrentRoute = () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  currentRoute.value = currentPage ? '/' + currentPage.route : ''
}

const isActive = (url) => {
  return currentRoute.value === url
}

onMounted(updateCurrentRoute)
onShow(updateCurrentRoute)

const goTab = (url) => {
  if (isActive(url)) return
  uni.redirectTo({ url });
};

const isLong = ref()
const goHome = ()=>{
  isLong.value = true
  uni.reLaunch({
    url: '/pages/index/index'
  })
}
</script>

<style lang="scss" scoped>
.custom-tabbar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 110rpx;
  padding-bottom: env(safe-area-inset-bottom);
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-around;
  box-shadow: 0 -2rpx 15rpx rgba(0, 0, 0, 0.06);
  z-index: 999;

  .tab-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 22rpx;
    color: #888;
    gap: 5rpx;
  }

  .tab-item-active {
    color: #2878ff;
    font-weight: bold;
  }

  .plus-item {
    position: relative;
  }

  .plus-circle {
    width: 100rpx;
    height: 100rpx;
    border-radius: 50%;
    background: #2878ff;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: -65rpx;
    box-shadow: 0 5rpx 15rpx rgba(40, 120, 255, 0.3);
    border: 8rpx solid #fff;
    transition: transform 0.15s ease;

  }
  .plus-item:active .plus-circle {
      transform: scale(0.85);
    }
  .plus {
    color: #fff;
    font-size: 65rpx;
    line-height: 1;
    margin-top: -7rpx;
  }
}
</style>
