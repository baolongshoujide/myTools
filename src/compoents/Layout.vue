<template>
        <view class="layout">
          <view class="content">
            <slot></slot>
          </view>

          <CustomTabBar />
        </view>
</template>
    
<script setup lang='ts'>
    import CustomTabBar from './CustomTabBar.vue';
</script>
    
<style lang="scss" scoped>
  .layout {
  min-height: 100vh;
}

.content {
  width: 100%;
  padding: 0 24rpx;
  padding-bottom: 220rpx;
  box-sizing: border-box;
}
</style>
