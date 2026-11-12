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
    .group-title {
      background-color: #fff5e9;
      color: #999999;
      font-size: 35rpx;
    }
    .group-content{
        background-color: #fff5e9;
    }
    
</style>
