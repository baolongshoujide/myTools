<template>
    <Layout>
      <view class="body">
      <Items v-for="item in list">
        <template #image>
          <image class="" :src="item.image">
            </image>
        </template>
        {{item.title}}</Items>
      
    </view>
    </Layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Items from './components/Items.vue';
import Layout from '@/compoents/Layout.vue';
const list = [
  {title:'幸运转盘',image:'/static/轮盘5.png'},
  {title:'连点器',image:'/static/轮盘5.png'},
  {title:'幸运转盘',image:'/static/轮盘5.png'},
  {title:'幸运转盘',image:'/static/轮盘5.png'},
  {title:'幸运转盘',image:'/static/轮盘5.png'}
]
</script>

<style lang="scss">
page{
    background-color: rgb(196, 202, 22);
}
 .body{
      padding:10rpx 24rpx ;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
    }
</style>
