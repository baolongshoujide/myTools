
<template>
  <view class="custom-tabbar">
    <!-- 首页 -->
    <view class="tab-item" @click="goTab('/pages/index/index')">
      <text class="tab-icon">⌂</text>
      <text>首页</text>
    </view>

    <!-- 功能 -->
    <view class="tab-item" @click="goTab('/pages/function/index')">
      <text class="tab-icon">▦</text>
      <text>功能</text>
    </view>

    <!-- 中间加号 -->
    <view class="tab-item plus-item" @click="openPublish">
      <view class="plus-circle">
        <text class="plus">＋</text>
      </view>
    </view>

    <!-- 我的 -->
    <view class="tab-item" @click="goTab('/pages/my/index')">
      <text class="tab-icon">♙</text>
      <text>我的</text>
    </view>
    <view class="tab-item" @click="goTab('/pages/my/index')">
      <text class="tab-icon">♙</text>
      <text>我的</text>
    </view>
  </view>
</template>

<script setup>
const goTab = (url) => {
  uni.redirectTo({ url });
};

const openPublish = () => {
 
};
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

  .tab-icon {
    font-size: 42rpx;
    line-height: 1.2;
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
  }

  .plus {
    color: #fff;
    font-size: 65rpx;
    line-height: 1;
    margin-top: -7rpx;
  }
}
</style>
