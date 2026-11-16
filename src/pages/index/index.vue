<template>
  <view class="main-shell">
    <swiper
      class="main-swiper"
      :current="navigation.nowTab"
      :duration="280"
      :circular="false"
      :indicator-dots="false"
      @change="changeTab"
    >
      <swiper-item>
        <scroll-view class="tab-scroll home-scroll" scroll-y>
          <view class="tab-content"><HomePanel /></view>
        </scroll-view>
      </swiper-item>
      <swiper-item>
        <scroll-view
          class="tab-scroll wheel-scroll"
          scroll-y
          :refresher-enabled="!navigation.locked"
          :refresher-triggered="refreshing"
          @refresherrefresh="restoreOrder"
        >
          <view class="tab-content">
            <Whell ref="wheelRef" @interaction-lock="navigation.setLocked" />
          </view>
        </scroll-view>
      </swiper-item>
      <swiper-item>
        <scroll-view class="tab-scroll" scroll-y>
          <view class="tab-content"><ListPanel /></view>
        </scroll-view>
      </swiper-item>
      <swiper-item>
        <scroll-view class="tab-scroll" scroll-y>
          <view class="tab-content"><MyPanel /></view>
        </scroll-view>
      </swiper-item>
    </swiper>
    <CustomTabBar />
    <view
      v-if="navigation.locked"
      class="interaction-mask"
      @touchstart.stop.prevent
      @touchmove.stop.prevent
      @touchend.stop.prevent
      @tap.stop.prevent
      @click.stop.prevent
    />
  </view>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { onHide, onLoad, onShow, onUnload } from '@dcloudio/uni-app'
import CustomTabBar from '@/compoents/CustomTabBar.vue'
import HomePanel from './components/HomePanel.vue'
import Whell from '../function/components/Whell.vue'
import ListPanel from '../list/components/ListPanel.vue'
import MyPanel from '../my/components/MyPanel.vue'
import { mainTabs, useNavigationStore } from '@/store/modules/navigation'
import { useWheelStore } from '@/store/modules/wheel'
import type { MainSwiperEvent } from '@/types/navigation'

const navigation = useNavigationStore()
const wheelStore = useWheelStore()
const wheelRef = ref<InstanceType<typeof Whell>>()
const refreshing = ref(false)
let refreshTimer: ReturnType<typeof setTimeout> | null = null
let visible = false

const updateTitle = () => {
  if (!visible) return
  uni.setNavigationBarTitle({
    title: navigation.nowTab === 1 ? wheelStore.nowWheel.name : mainTabs[navigation.nowTab].title,
  })
}

const changeTab = (event: MainSwiperEvent) => {
  navigation.selectTab(event.detail.current)
}

const restoreOrder = () => {
  if (refreshing.value) return

  refreshing.value = true
  wheelRef.value?.restorePrizeOrder()

  // 等原生 scroll-view 的下拉刷新动画收尾后再解除 refreshing，
  // 避免刷新手势还没结束时紧接着的点击被滚动层吞掉。
  refreshTimer = setTimeout(() => {
    refreshing.value = false
    refreshTimer = null
  }, 500)
}

watch(() => [navigation.nowTab, wheelStore.nowWheel.name], updateTitle)

onLoad((options) => {
  if (options?.tab !== undefined) navigation.selectTab(Number(options.tab))
})

onShow(() => {
  visible = true
  updateTitle()
})

onHide(() => { visible = false })
onUnload(() => {
  navigation.setLocked(false)
  if (refreshTimer) {
    clearTimeout(refreshTimer)
    refreshTimer = null
  }
})
</script>

<style lang="scss" scoped>
.main-shell {
  height: calc(100vh - var(--window-top, 0px) - var(--window-bottom, 0px));
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f5f7fb;
}
.main-swiper {
  flex: 1;
  min-height: 0;
  width: 100%;
  margin-bottom: calc(110rpx + env(safe-area-inset-bottom));
}
.tab-scroll {
  height: 100%;
  width: 100%;
  background: #f5f7fb;
}
.tab-content {
  padding: 0 24rpx calc(64rpx + env(safe-area-inset-bottom));
  box-sizing: border-box;
  min-height: 100%;
}
.wheel-scroll {
  background: #fff5e9;
}
.interaction-mask {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 10000;
  background: transparent;
  pointer-events: auto;
}
</style>
