<template>
        <slot></slot>
        <CustomTabBar></CustomTabBar>
</template>
    
<script setup lang='ts'>
    import CustomTabBar from './CustomTabBar.vue';
</script>
    
<style lang="scss">
    .layout {
  min-height: 100vh;
  position: relative;
}

.layout-content {
  padding-bottom: 140rpx;
}
</style>