<template>
  <Layout>
    <view class="wheel-list">
      <Item v-for="item in 6" :key="item" />
    </view>
  </Layout>
</template>

<script lang="ts" setup>
import Layout from '@/compoents/Layout.vue'
import Item from './components/Item.vue'
</script>

<style scoped>
.wheel-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding-top: 24rpx;
}
</style>
