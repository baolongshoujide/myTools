<template>
 <Layout class="wheel-layout">
  <Whell ref="wheelRef"></Whell>
  
 </Layout>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { onPullDownRefresh,onShow } from '@dcloudio/uni-app'
import Whell from './components/Whell.vue';
import Layout from '@/compoents/Layout.vue';
import { useWheelStore } from '@/store/modules/wheel';

const wheelRef = ref()
const wheelStore = useWheelStore()

onPullDownRefresh(() => {
  wheelRef.value?.restorePrizeOrder()
  uni.stopPullDownRefresh()
})

onShow(()=>{
  uni.setNavigationBarTitle({
    title:wheelStore.nowWheel.name,
  })
})

</script>

<style scoped>
.wheel-layout {
  background-color: #fff5e9;
}
</style>
