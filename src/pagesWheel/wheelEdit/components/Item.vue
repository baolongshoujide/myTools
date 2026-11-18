<template>
       <uni-group
        :top="20"
        class="wheel-group"
      >
       <template #title>
           <view class="group-title">
             <slot name="title"></slot>
           </view>
        </template>
        
          <view class="group-content">
    <!-- 表单内容 -->
            <slot></slot>
          </view>
      </uni-group> 
</template>
    
<script setup lang='ts'>
    
</script>
    
<style lang="scss" scoped>
    .wheel-group {
      :deep(.uni-group__content) {
        background: var(--dragon-surface);
      }
    }
    .group-title {
      background-color: var(--dragon-surface);
      color: var(--dragon-muted);
      font-size: 35rpx;
    }
    .group-content{
        background-color: var(--dragon-surface);
    }
    
</style>
