
<template>
  <view class="page">
    <view class="wheel-container">
      <!-- 圆盘 -->
      <view class="wheel" :style="{background:wheelBackground,transform: `rotate(${rotate}deg)`, transitionDuration: `${wheelStore.spinTime}s`}">
        <!-- 六个奖项文字 -->
        <view
          v-for="(item, index) in wheelStore.prizes"
          :key="index"
          class="prize"
          :style="{
              transform: `translate(-50%, -50%)
                rotate(${index * (360 / wheelStore.prizes.length) + (180 / wheelStore.prizes.length)}deg)
                translateY(-32vw)
                `
            }"
        >
          {{ item }}
        </view>

        <!-- 中间按钮 -->
        
      </view>
      <view class="center-button" @tap="spin">
        <view class="pointer"></view>
          GO
      </view>
      
    </view>
    <view class="footer">
        <uni-icons
        type="gear"
        color=""
        size="45"
        @tap="uni.navigateTo({url:`/pagesWheel/wheelSetting/index`})"
      />
      <uni-icons
        type="loop"
        color=""
        size="45"
      />
      <uni-icons
        type="compose"
        color=""
        size="45"
        @tap="uni.navigateTo({url:`/pagesWheel/wheelEdit/index`})"

      />
      </view>
  </view>
  <view v-if="isSpinning" class="spin-mask"></view>
</template>


<script setup>
import { computed, ref } from 'vue'
import { useWheelStore } from '@/store/modules/wheel'

const wheelStore = useWheelStore()

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
function getPrizeColor(index) {
  const colorIndex = colorOrder[index % colorOrder.length]
  return colors[colorIndex]
}

// 根据奖品数量动态生成转盘背景
const wheelBackground = computed(() => {
  const one = 360 / wheelStore.prizes.length

  const everybig = wheelStore.prizes.map((item, index) => {
    const start = one * index
    const end = one * (index + 1)

    return `${getPrizeColor(index)} ${start}deg ${end}deg`
  })

  return `conic-gradient(${everybig.join(', ')})`
})

// 转盘旋转角度
const rotate = ref(0)

// 是否正在旋转
const isSpinning = ref(false)

// 点击开始抽奖
function spin() {

  // 如果正在旋转，就不允许再次点击
  if (isSpinning.value) {
    return
  }

  // 开始旋转
  isSpinning.value = true

  // 随机选择一个奖项
  const index = Math.floor(Math.random() * wheelStore.prizes.length)

  // 每个奖项占据的角度
  const anglePerPrize = 360 / wheelStore.prizes.length

  // 计算中奖区域的中心角度
  const prizeCenterAngle = index * anglePerPrize + anglePerPrize / 2

  // 当前圆盘角度
  const currentAngle = rotate.value % 360

  // 计算需要补转的角度
  const alignAngle = (
    360 - (prizeCenterAngle + currentAngle) % 360
  ) % 360

  // 再转5圈，然后对准中奖区域
  rotate.value += 5 * 360 + alignAngle

  // 等待动画结束
  setTimeout(() => {

    isSpinning.value = false

    // 显示中奖结果
    uni.showModal({
      title: '抽奖结果',
      content: `恭喜你获得：${wheelStore.prizes[index]}`,
      showCancel: false
    })

  }, wheelStore.spinTime * 1000)
}
</script>


<style lang="scss" scoped>
.page{
     min-height: 100vh;
     background: #fff5e9;
     .wheel-container{
        width: 100vw;
        height: 100vw;
        background-color: pink;
        position:relative;
        .wheel{
            width: 86%;
            height: 86%;
            background-color: red;
            border-radius: 50%;
            position: absolute;
            left: 7%;
            top: 7%;
            border: 6rpx solid #ffb52e;
            box-sizing: border-box;
             transition: transform 5s cubic-bezier(0.12, 0.75, 0.15, 1);
            .prize{
                position: absolute;
                left: 50%;
                top: 50%;
                width: 200rpx;
                text-align: center;
                font-size: 90%;
                font-weight: bold;
                color: #fff;
            }
            
        }
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
                            
                display: flex;
                justify-content: center;
                align-items: center;
                            
                color: #ff7043;
                font-size: 50rpx;
                font-weight: bold;
                z-index: 2;
                }
                
        .pointer {
             position: absolute;
             top: -49rpx;
             left: 50%;
             transform: translateX(-50%);
             z-index: 3;
                    
             width: 0;
             height: 0;
                    
             border-left: 13px solid transparent;
             border-right: 13px solid transparent;
             border-bottom: 22px solid #ffb52e;
            }
     }
     .footer{
      width: 100%;
      display: flex;
      justify-content: space-around;
      padding: 30rpx;
      box-sizing: border-box;
      uni-icons{
        padding: 30rpx;
        height: 100%;
        background-color: #e0d7d7;
        border-radius: 50%;

      }
     }
}
.spin-mask {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background: transparent;
}
</style>
