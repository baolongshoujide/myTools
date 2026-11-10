
<template>
  <view class="page">
    <view class="wheel-container">
      <!-- 圆盘 -->
      <view class="wheel" :style="{background:wheelBackground,transform: `rotate(${rotate}deg)`}">
        <!-- 六个奖项文字 -->
        <view
          v-for="(item, index) in prizes"
          :key="index"
          class="prize"
          :style="{
              transform: `translate(-50%, -50%)
                rotate(${index * (360 / prizes.length) + (180 / prizes.length)}deg)
                translateY(-32vw)
                `
            }"
        >
          {{ item }}
        </view>

        <!-- 中间按钮 -->
        
      </view>
    <view class="center-button" @tap="spin">
          GO
        </view>
      <!-- 顶部指针 -->
      <view class="pointer"></view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue';

const prizes = [
  '一等奖',
  '二等奖',
  '三等奖',
  '谢谢参与',
  '幸运奖',
  '再来一次',
]
// 每个奖项对应一种颜色
const colors = [
  '#ff6868',
  '#ffcf52',
  '#65c8a5',
  '#58a9ed',
  '#a68aec',
  '#ff9b50'
]
const wheelBackground = computed(()=>{
    const one = 360 /prizes.length
    const everybig = prizes.map((item,index) =>{
        const start = one * index
        const end = one *(index+1)
        return `${colors[index % colors.length]} ${start}deg ${end}deg`
    })
    return `conic-gradient(${everybig.join(', ')})`
})

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
  const index = Math.floor(Math.random() * prizes.length)

  // 每个奖项占60度
  const anglePerPrize = 360 / prizes.length

  // 计算中奖区域的中心角度
  const prizeCenterAngle = index * anglePerPrize + anglePerPrize / 2

  // 当前圆盘角度
  const currentAngle = rotate.value % 360

  // 计算需要补转多少度，让中奖区域对准指针
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
      content: `恭喜你获得：${prizes[index]}`,
      showCancel: false
    })

  }, 5000)
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
                border: 5rpx solid #ffb52e;
                            
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
             top: 10rpx;
             left: 50%;
             transform: translateX(-50%);
             z-index: 3;
                    
             width: 0;
             height: 0;
                    
             border-left: 13px solid transparent;
             border-right: 13px solid transparent;
             border-top: 25px solid #e94335;
            }
     }
}
</style>
