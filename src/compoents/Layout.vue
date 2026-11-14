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
    
<style lang="scss">
  .layout {
  min-height: 100vh;
}

.content {
  padding-bottom: 220rpx;
}
</style>