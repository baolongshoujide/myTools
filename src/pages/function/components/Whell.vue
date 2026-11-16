
<template>
  <view class="page">

    <!-- 当前指针经过的奖项：单独占一行 -->
    <view class="now-prize">
      {{ displayPrizes[displayIndex] || '' }}
    </view>

    <!-- 正方形转盘区域 -->
    <view class="wheel-stage">

      <!-- 圆盘 -->
      <view
        class="wheel"
        @longpress.stop="deletePrizeAtPosition"
        :style="{
          background: wheelBackground,
          transform: `rotate(${rotate}deg)`
        }"
      >
        <!-- 奖项文字 -->
        <view
          v-for="(item, index) in displayPrizes"
          :key="index"
          class="prize"
          :style="{
            transform: `
              rotate(${index * (360 / displayPrizes.length) + (180 / displayPrizes.length)}deg)
            `
          }"
        >
          <text class="prize-label">{{ item }}</text>
        </view>
      </view>

      <!-- 中间按钮 -->
      <view class="center-button" @tap="spin">
        <view class="pointer"></view>
        GO
      </view>

      <!-- 指针：独立于中心按钮 -->
      

    </view>

    <!-- 底部操作 -->
    <view class="footer">
      <view
        class="footer-button"
        hover-class="footer-button-active"
        :hover-stay-time="150"
        @tap="openSettings"
      >
        <uni-icons type="gear" size="45" />
      </view>

      <view
        class="footer-button"
        hover-class="footer-button-active"
        :hover-stay-time="150"
        @tap="change"
      >
        <uni-icons type="loop" size="45" />
      </view>

      <view
        class="footer-button"
        hover-class="footer-button-active"
        :hover-stay-time="150"
        @tap="Go('/pagesWheel/wheelEdit/index')"
      >
        <uni-icons type="compose" size="45" />
      </view>
    </view>
      <uni-popup
        ref="settingsPopup"
        type="bottom"
        background-color="#ffffff"
        border-radius="24px 24px 0 0"
        :is-mask-click="true"
        style="z-index: 10020;"
      >
        <view class="settings-panel">
          <view class="settings-handle" />
          <view class="settings-header">
            <text class="settings-title">转盘设置</text>
            <button class="settings-close" hover-class="none" @tap="closeSettings">
              <uni-icons type="closeempty" :size="24" color="#7b8798" />
            </button>
          </view>
          <scroll-view class="settings-content" scroll-y>
              <view class="settings-list">

                <view class="setting-item flex-between">
                  <view class="setting-text">
                    <uni-icons class="setting-icon" type="phone" color="#3d8efe" size="24" />
                    震动
                  </view>
                  <switch
                    :checked="wheelStore.settings.dong"
                    @change="updateSetting('dong')"
                    color="#3d8efe"
                  />
                </view>

                <view class="setting-item flex-between">
                  <view class="setting-text">
                    <uni-icons class="setting-icon" type="loop" color="#3d8efe" size="24" />
                    不重复抽取
                  </view>
                  <switch
                    :checked="wheelStore.settings.noRepeat"
                    @change="updateSetting('noRepeat')"
                    color="#3d8efe"
                  />
                </view>

                <view class="setting-item flex-between">
                  <view class="setting-text">
                    <uni-icons class="setting-icon" type="chatbubble" color="#3d8efe" size="24" />
                    转盘结果弹窗
                  </view>
                  <switch
                    :checked="wheelStore.settings.showModal"
                    @change="updateSetting('showModal')"
                    color="#3d8efe"
                  />
                </view>

                <view class="setting-item flex-between">
                  <view class="setting-text setting-text-disabled">
                    <uni-icons class="setting-icon" type="mic" color="#3d8efe" size="24" />
                    语音播报（暂未启用）
                  </view>
                  <switch :checked="false" disabled color="#3d8efe" />
                </view>
              </view>
          </scroll-view>
        </view>
      </uni-popup>

  </view>
</template>


<script setup lang="ts">
import { computed, getCurrentInstance, nextTick, onUnmounted, ref, watch } from 'vue'
import { useWheelStore } from '@/store/modules/wheel'
import type { Settings, WheelAnimationTimer, WheelPressEvent, WheelPopupInstance } from '@/types/wheel'
import { getPrizeIndex } from '../wheelGeometry'

const wheelStore = useWheelStore()
const emit = defineEmits({
  'interaction-lock': (locked: boolean) => typeof locked === 'boolean',
})
const instance = getCurrentInstance()
const deleteDialogOpen = ref(false)
const settingsPopup = ref<WheelPopupInstance>()
const drawnPrizes = ref<Set<string>>(new Set())
// 转盘当前显示的顺序单独保存，避免打乱时改动编辑页保存的原顺序
const displayPrizes = ref(wheelStore.nowWheel.prizes.slice())

watch(
  () => wheelStore.nowWheel.prizes,
  (prizes) => {
    displayPrizes.value = prizes.slice()
    drawnPrizes.value = new Set()
    updateDisplayIndex()
  }
)

watch(() => wheelStore.nowWheel.id, () => {
  drawnPrizes.value = new Set()
})

watch(() => wheelStore.settings.noRepeat, (enabled) => {
  if (!enabled) drawnPrizes.value = new Set()
})

// 预设 12 种颜色
const colors = [
  '#ff6868',
  '#ffcf52',
  '#65c8a5',
  '#58a9ed',
  '#a68aec',
  '#ff9b50',
  '#e8798e',
  '#42c5c5',
  '#8068d9',
  '#b8d957',
  '#d477bc',
  '#557bea'
]

// 颜色分配顺序
const colorOrder = [
  0, 6, 3, 9,
  1, 7, 4, 10,
  2, 8, 5, 11
]

// 根据奖品索引获取颜色
const getPrizeColor = (index: number) => {
  const colorIndex = colorOrder[index % colorOrder.length]
  return colors[colorIndex]
}

// 根据奖品数量动态生成转盘背景
const wheelBackground = computed(() => {
  const prizes = displayPrizes.value

  if (!prizes.length) {
    return '#eeeeee'
  }

  const one = 360 / prizes.length

  const everybig = prizes.map((item, index) => {
    const start = one * index
    const end = one * (index + 1)

    return `${getPrizeColor(index)} ${start}deg ${end}deg`
  })

  return `conic-gradient(${everybig.join(', ')})`
})

// 转盘当前旋转角度
const rotate = ref(0)

// 是否正在旋转
const isSpinning = ref(false)

// 转盘旋转及删除确认期间禁止操作背景页面。
watch([isSpinning, deleteDialogOpen], ([spinning, deleting]) => {
  emit('interaction-lock', spinning || deleting)
}, { flush: 'sync' })

const openSettings = () => {
  if (isSpinning.value || deleteDialogOpen.value) return
  settingsPopup.value?.open()
}

const closeSettings = () => {
  settingsPopup.value?.close()
}

const updateSetting = (setting: keyof Settings) => {
  wheelStore.settings[setting] = !wheelStore.settings[setting]
}

// 最终中奖索引
const index = ref(0)

// 当前指针经过的奖项索引
const displayIndex = ref(999)

// 保存动画定时器，方便清理
let animationTimer: WheelAnimationTimer = null

const deletePrizeAtPosition = (event: WheelPressEvent) => {
  if (isSpinning.value || deleteDialogOpen.value || !instance?.proxy) return
  if (displayPrizes.value.length <= 2) {
    uni.showToast({ title: '至少保留两个奖项', icon: 'none' })
    return
  }
  const touch = event.touches?.[0] || event.changedTouches?.[0]
  if (!touch) return
  uni.createSelectorQuery().in(instance.proxy).select('.wheel-stage').boundingClientRect((rect) => {
    if (!rect || Array.isArray(rect) || isSpinning.value || deleteDialogOpen.value) return
    if (typeof rect.left !== 'number' || typeof rect.top !== 'number' || typeof rect.width !== 'number' || rect.width <= 0) return
    const prizeIndex = getPrizeIndex(touch.clientX - rect.left, touch.clientY - rect.top, rect.width, rotate.value, displayPrizes.value.length)
    if (prizeIndex < 0) return
    const name = displayPrizes.value[prizeIndex]
    const wheel = wheelStore.nowWheel
    const savedPrizes = wheel.prizes
    // 显示顺序可能已打乱，按名称找到存档中的对应奖项；同名奖项只删一个。
    const savedIndex = savedPrizes.indexOf(name)
    if (savedIndex < 0) return
    const remaining = displayPrizes.value.slice()
    remaining.splice(prizeIndex, 1)
    deleteDialogOpen.value = true
    uni.showModal({
      title: '删除奖项',
      content: '确定删除「' + name + '」吗？',
      confirmText: '删除',
      confirmColor: '#e54d42',
      success: async (result) => {
        if (!result.confirm || isSpinning.value) return
        if (wheelStore.nowWheel.id !== wheel.id || wheelStore.nowWheel.prizes !== savedPrizes) {
          uni.showToast({ title: '转盘已更新，请重新长按', icon: 'none' })
          return
        }
        if (!wheelStore.removePrize(wheel.id, savedIndex)) return
        // 等待 store 的监听更新完毕，再保留剩余奖项当前的显示顺序。
        await nextTick()
        displayPrizes.value = remaining
        updateDisplayIndex()
        uni.showToast({ title: '奖项已删除', icon: 'success' })
      },
      complete: () => { deleteDialogOpen.value = false },
    })
  }).exec()
}


// 根据转盘实时角度计算指针指向哪个奖项
const updateDisplayIndex = () => {
  const prizes = displayPrizes.value

  if (!prizes.length) return

  const anglePerPrize = 360 / prizes.length

  // 将旋转角度转换为 0 ~ 360
  const nowAngle = ((rotate.value % 360) + 360) % 360

  // 指针固定在顶部，所以需要反向计算
  const pointerAngle = (360 - nowAngle) % 360

  // 得到当前指针对应的奖项索引
  const nextDisplayIndex = Math.floor(pointerAngle / anglePerPrize)
  const hasEnteredNextPrize = displayIndex.value !== 999 && displayIndex.value !== nextDisplayIndex
  displayIndex.value = nextDisplayIndex

  // 只在动画经过扇区边界时轻震；初始化、整理顺序时不触发。
  if (isSpinning.value && hasEnteredNextPrize && wheelStore.settings.dong) {
    uni.vibrateShort({ type: 'light' })
  }
}


// cubic-bezier 缓动函数
// 对应 CSS：cubic-bezier(0.12, 0.75, 0.15, 1)
const cubicBezier = (progress: number) => {
  const x1 = 0.12
  const y1 = 0.75
  const x2 = 0.15
  const y2 = 1

  // 根据 t 计算贝塞尔曲线的坐标
  const bezier = (t: number, a: number, b: number) => {
    const c = 3 * a
    const d = 3 * (b - a) - c
    const e = 1 - c - d

    return ((e * t + d) * t + c) * t
  }

  // 根据 x 找到对应的 t
  let low = 0
  let high = 1
  let t = progress

  // 二分法求解
  for (let i = 0; i < 20; i++) {
    t = (low + high) / 2

    const x = bezier(t, x1, x2)

    if (x < progress) {
      low = t
    } else {
      high = t
    }
  }

  // 根据 t 得到 y
  return bezier(t, y1, y2)
}


// 执行转盘动画
const startAnimation = (
  startAngle: number,
  endAngle: number,
  duration: number
) => {
  return new Promise<void>((resolve) => {
    const startTime = Date.now()

    const animate = () => {
      const elapsed = Date.now() - startTime

      // 动画进度 0 ~ 1
      const progress = Math.min(elapsed / duration, 1)

      // 使用缓动曲线计算当前动画进度
      const easedProgress = cubicBezier(progress)

      // 更新转盘实时角度
      rotate.value =
        startAngle + (endAngle - startAngle) * easedProgress

      // 根据当前真实角度更新奖项
      updateDisplayIndex()

      // 动画结束
      if (progress >= 1) {
        rotate.value = endAngle

        // 确保最终显示中奖奖项
        displayIndex.value = index.value

        resolve()
        return
      }

      // 下一帧继续执行
      animationTimer = setTimeout(animate, 16)
    }

    animate()
  })
}


// 点击开始抽奖
const spin = async () => {

  // 正在旋转时不允许再次点击
  if (isSpinning.value || deleteDialogOpen.value) {
    return
  }

  const prizes = displayPrizes.value.slice()

  // 没有奖项时不允许抽奖
  if (!prizes.length) {
    uni.showToast({
      title: '请先添加奖项',
      icon: 'none'
    })
    return
  }

  // 获取旋转时间
  const spinTime = Number(wheelStore.nowWheel.spinTime)

  if (!Number.isFinite(spinTime) || spinTime <= 0) {
    uni.showToast({
      title: '旋转时间设置不正确',
      icon: 'none'
    })
    return
  }

  isSpinning.value = true

  // 随机选择最终中奖索引
  let availableIndexes = prizes.map((_item, prizeIndex) => prizeIndex)

  if (wheelStore.settings.noRepeat) {
    const notDrawnIndexes = availableIndexes.filter(
      (prizeIndex) => !drawnPrizes.value.has(prizes[prizeIndex])
    )

    if (notDrawnIndexes.length > 0) {
      availableIndexes = notDrawnIndexes
    } else {
      // 本轮奖项都抽过后，自动开始新一轮。
      drawnPrizes.value = new Set()
    }
  }

  index.value = availableIndexes[Math.floor(Math.random() * availableIndexes.length)]

  // 每个奖项占据的角度
  const anglePerPrize = 360 / prizes.length

  // 中奖区域的中心角度
  const prizeCenterAngle =
    index.value * anglePerPrize + anglePerPrize / 2

  // 当前转盘角度
  const nowAngle = ((rotate.value % 360) + 360) % 360

  // 计算需要补转的角度
  const alignAngle =
    (360 - (prizeCenterAngle + nowAngle) % 360) % 360

  // 起始角度
  const startAngle = rotate.value

  // 再转 5 圈，然后停在中奖区域中心
  const endAngle = startAngle + 5 * 360 + alignAngle

  try {
    // 开始动画，等待动画结束
    await startAnimation(
      startAngle,
      endAngle,
      spinTime * 1000
    )

    const winningPrize = prizes[index.value]

    if (wheelStore.settings.noRepeat) {
      drawnPrizes.value.add(winningPrize)
    }

    if (wheelStore.settings.showModal) {
      // 等结果弹窗关闭后再解除旋转锁，避免弹窗仍遮挡页面时误以为底部按钮失效。
      await new Promise<void>((resolve) => {
        uni.showModal({
          title: '抽奖结果',
          content: `恭喜你获得：${winningPrize}`,
          showCancel: false,
          complete: () => resolve(),
        })
      })
    }

  } finally {
    isSpinning.value = false
    animationTimer = null
  }
}

// 随机更换奖项位置
const change = () => {
  if (isSpinning.value) return

  const originalPrizes = displayPrizes.value.slice()
  const prizes = originalPrizes.slice()

  // 随机交换奖项位置
  for (let i = prizes.length - 1; i > 0; i--) {
    const randomIndex = Math.floor(Math.random() * (i + 1))

    ;[prizes[i], prizes[randomIndex]] = [
      prizes[randomIndex],
      prizes[i]
    ]
  }

  // 随机结果可能刚好和原顺序相同；有不同奖项时强制交换一次，避免看起来像按钮没响应。
  const hasSameOrder = prizes.every((item, prizeIndex) => item === originalPrizes[prizeIndex])
  if (hasSameOrder) {
    const differentPrizeIndex = prizes.findIndex((item) => item !== prizes[0])
    if (differentPrizeIndex > 0) {
      ;[prizes[0], prizes[differentPrizeIndex]] = [
        prizes[differentPrizeIndex],
        prizes[0],
      ]
    }
  }

  // 只更新当前显示顺序，不覆盖原始奖项顺序
  displayPrizes.value = prizes

  // 根据当前指针位置刷新奖项文字
  updateDisplayIndex()
  displayIndex.value=999
}

// 下拉刷新时恢复编辑页保存的原始顺序
const restorePrizeOrder = () => {
  if (isSpinning.value) return

  displayPrizes.value = wheelStore.nowWheel.prizes.slice()
  updateDisplayIndex()
  displayIndex.value=999
}

defineExpose({
  restorePrizeOrder,
})

// 页面销毁时清理动画
onUnmounted(() => {
  emit('interaction-lock', false)
  if (animationTimer) {
    clearTimeout(animationTimer)
    animationTimer = null
  }
})

const Go = (setUrl:string)=>{
  if (isSpinning.value || deleteDialogOpen.value) return
  uni.navigateTo({
    url: setUrl
  })
}

</script>


<style lang="scss" scoped>
.page {
  width: 100%;
  background: #fff5e9;

  // 当前奖项标题
  .now-prize {
    width: 100%;
    height: 100rpx;

    display: flex;
    justify-content: center;
    align-items: center;

    font-size: 32rpx;
    font-weight: bold;
    color: #ff7043;
  }

  // 正方形转盘容器
  .wheel-stage {
    width: 100%;
    height: 0;
    // 百分比内边距根据容器宽度计算，使转盘保持正方形
    padding-bottom: 100%;
    margin: 20rpx auto 48rpx;
    position: relative;

    // 圆盘
    .wheel {
      width: 100%;
      height: 100%;

      position: absolute;
      left: 0;
      top: 0;

      border-radius: 50%;
      border: 6rpx solid #ffb52e;
      box-sizing: border-box;

      // JS 控制旋转，不设置 transition

      .prize {
        position: absolute;
        left: 0;
        top: 0;

        width: 100%;
        height: 100%;
        text-align: center;

        font-size: 90%;
        font-weight: bold;
        color: #fff;

        .prize-label {
          position: absolute;
          left: 50%;
          top: 13%;
          width: 200rpx;
          transform: translate(-50%, -50%);
        }
      }
    }

    // 中心按钮
    .center-button {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);

      width: 150rpx;
      height: 150rpx;

      border-radius: 50%;
      background: #fff;
      border: 10rpx solid #ffb52e;
      box-sizing: border-box;

      display: flex;
      justify-content: center;
      align-items: center;

      color: #ff7043;
      font-size: 50rpx;
      font-weight: bold;
      z-index: 2;
    }

    // 顶部指针
    .pointer {
      position: absolute;
      top: -47rpx;
      left: 50%;
      transform: translateX(-50%);
      z-index: 3;

      width: 0;
      height: 0;

      // 三角形尖端朝下
      border-left: 13px solid transparent;
      border-right: 13px solid transparent;
      border-bottom: 22px solid #ffb52e;
    }
  }

  // 底部操作
  .footer {
    position: relative;
    z-index: 5;
    width: 100%;

    display: flex;
    justify-content: space-around;
    align-items: center;

    padding: 30rpx;
    box-sizing: border-box;

    .footer-button {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 30rpx;
      background-color: #e0d7d7;
      border-radius: 50%;
      transition: transform 0.15s ease;
    }

    .footer-button-active {
      transform: scale(0.85);
    }
  }
}

.settings-panel {
  padding: 20rpx 32rpx 28rpx;
  box-sizing: border-box;

  .settings-handle {
    width: 72rpx;
    height: 8rpx;
    margin: 0 auto 24rpx;
    border-radius: 8rpx;
    background: #e2e7ef;
  }

  .settings-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24rpx;
  }

  .settings-title {
    font-size: 34rpx;
    font-weight: 600;
    color: #2c3a52;
  }

  .settings-close {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 64rpx;
    height: 64rpx;
    padding: 0;
    margin: 0;
    border-radius: 50%;
    background: #f2f5f9;
  }

  .settings-content {
    height: 60vh;
  }

  .settings-done {
    margin-top: 24rpx;
    border-radius: 20rpx;
    font-size: 30rpx;
    color: #fff;
    background: #2878ff;
  }

  .settings-close::after,
  .settings-done::after {
    border: none;
  }
}

.settings-list {
  .setting-item {
    min-height: 70rpx;
    margin-bottom: 20rpx;
    padding: 10rpx;
    border-radius: 15rpx;
    background-color: #e0dcdc;

    .setting-text {
      display: flex;
      align-items: center;
      font-size: 45rpx;

      .setting-icon {
        margin-right: 12rpx;
      }
    }

    .setting-text-disabled {
      color: #a0a0a0;
    }
  }
}
</style>
