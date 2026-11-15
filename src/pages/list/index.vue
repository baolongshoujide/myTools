<template>
  <Layout>
    <view class="wheel-list">
      <Item :prop = item v-for="item in wheelStore.wheels" :key="item.id" />
    </view>
  </Layout>
</template>

<script lang="ts" setup>
import Layout from '@/compoents/Layout.vue'
import Item from './components/Item.vue'
import { useWheelStore } from '@/store/modules/wheel';

const wheelStore = useWheelStore()

console.log(wheelStore.wheels);

</script>

<style scoped>
.wheel-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding-top: 24rpx;
}
</style>
