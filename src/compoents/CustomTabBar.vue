
<template>
  <view class="custom-tabbar">
    <!-- 首页 -->
    <view class="tab-item" :class="{ 'tab-item-active': isActive('/pages/index/index') }" @click="goTab('/pages/index/index')">
      <uni-icons type="home" size="24" :color="isActive('/pages/index/index') ? '#2878ff' : '#888'" />
      <text>首页</text>
    </view>

    <!-- 功能 -->
    <view class="tab-item" :class="{ 'tab-item-active': isActive('/pages/function/index') }" @click="goTab('/pages/function/index')">
      <uni-icons type="bars" size="24" :color="isActive('/pages/function/index') ? '#2878ff' : '#888'" />
      <text>功能</text>
    </view>

    <!-- 中间加号 -->
    <view class="tab-item plus-item" @tap="openAddMenu" @touchstart="isLong = false" @longpress="goHome">
       <view class="plus-circle">
          <uni-icons
            v-if="isLong"
            type="home"
            size="30"
            color="#fff"
          />
       <text v-else class="plus">＋</text>
       </view>
    </view>
    <!-- 列表 -->
    <view class="tab-item" :class="{ 'tab-item-active': isActive('/pages/list/index') }" @click="goTab('/pages/list/index')">
  <uni-icons
    type="list"
    size="24"
    :color="isActive('/pages/list/index') ? '#2878ff' : '#888'"
  />
  <text>列表</text>
</view>
    <view class="tab-item" :class="{ 'tab-item-active': isActive('/pages/my/index') }" @click="goTab('/pages/my/index')">
      <uni-icons type="person" size="24" :color="isActive('/pages/my/index') ? '#2878ff' : '#888'" />
      <text>我的</text>
    </view>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app';
import { onMounted, ref } from 'vue';
import { useWheelStore } from '@/store/modules/wheel';

const wheelStore = useWheelStore()

const nowRoute = ref('')

const updateNowRoute = () => {
  const pages = getCurrentPages()
  const nowPage = pages[pages.length - 1]
  nowRoute.value = nowPage ? '/' + nowPage.route : ''
}

const isActive = (url) => {
  return nowRoute.value === url
}

onMounted(updateNowRoute)
onShow(updateNowRoute)

const goTab = (url) => {
  if (isActive(url)) return
  uni.redirectTo({ url });
};

const isLong = ref()
const createWheel = () => {
  uni.navigateTo({ url: '/pagesWheel/wheelEdit/index?mode=create' })
}

const addWheelPrize = () => {
  const item = wheelStore.nowWheel
  if (!item) {
    uni.showToast({ title: '请先创建转盘', icon: 'none' })
    return
  }
  const wheelId = item.id
  uni.showModal({
    title: '添加到「' + item.name + '」',
    editable: true,
    placeholderText: '请输入奖项名称',
    success: (result) => {
      if (!result.confirm) return
      if (!wheelStore.addPrize(wheelId, result.content || '')) {
        uni.showToast({ title: '请输入有效的奖项名称', icon: 'none' })
        return
      }
      uni.showToast({ title: '奖项已添加', icon: 'success' })
    },
  })
}

// 加号根据当前页面分配操作。
// 连点器页面做好后，在这里接入：功能页 → 添加单个操作，列表页 → 新建方案。
const addActions = {
  '/pages/list/index': createWheel,
  '/pages/function/index': addWheelPrize,
}

const openAddMenu = () => {
  if (isLong.value) return
  updateNowRoute()
  const action = addActions[nowRoute.value]
  if (action) {
    action()
    return
  }
  uni.showActionSheet({
    itemList: ['添加奖项', '新建转盘'],
    success: (response) => {
      if (response.tapIndex === 1) {
        createWheel()
        return
      }
      addWheelPrize()
    },
  })
}

const goHome = ()=>{
  isLong.value = true
  uni.reLaunch({
    url: '/pages/index/index'
  })
}
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

  .tab-item-active {
    color: #2878ff;
    font-weight: bold;
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
    transition: transform 0.15s ease;

  }
  .plus-item:active .plus-circle {
      transform: scale(0.85);
    }
  .plus {
    color: #fff;
    font-size: 65rpx;
    line-height: 1;
    margin-top: -7rpx;
  }
}
</style>
