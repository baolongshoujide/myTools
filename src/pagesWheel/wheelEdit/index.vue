<template>
  <view class="wheel-edit">
    <Item>
      <template #title>轮盘标题</template>
      <MyInput v-model="backupWheel.name" placeholder="请输入轮盘名称" />
    </Item>

    <Item>
      <view class="time-row">
        <text class="time-label">旋转时间（秒）</text>
        <uni-number-box
          v-model="backupWheel.spinTime"
          :min="1"
          :max="9"
          :width="30"
        />
      </view>
    </Item>

    <Item>
      <template #title>
        <view class="prize-heading">
          <text>奖品选项</text>
        </view>
      </template>

      <view
        v-for="(prize, index) in backupWheel.prizes"
        :key="index"
        class="prize-row"
      >
        <MyInput
          v-model="backupWheel.prizes[index]"
          class="prize-input"
          :placeholder="`奖项${index + 1}`"
        >
          <template #left>
            <image
              class="prefix-icon"
              :class="{ 'delete-icon-disabled': backupWheel.prizes.length <= 2 }"
              src="/static/delete.png"
              mode="aspectFit"
              @tap.stop="removePrize(index)"
            />
          </template>
        </MyInput>
        
      </view>
      <view class="action-row" @tap="addPrize()">
        <MyInput
          placeholder="添加新选项"
          placeholder-style="color:#2979FF;font-size:18px"
          disabled
        >
          <template #left>
            <image class="prefix-icon" src="/static/添加.png" mode="aspectFit" />
          </template>
        </MyInput>
      </view>
      <view class="action-row">
        <MyInput
          placeholder="批量添加选项"
          placeholder-style="color:#2979FF;font-size:18px"
           readonly
          @tap="popup.open()"
        >
          <template #left>
            <image class="prefix-icon" src="/static/批量添加.png" mode="aspectFit" />
          </template>
        </MyInput>
      </view>
    </Item>

    <text class="hint">至少保留两个奖项；保存后同步到转盘。</text>
    <view class="prize-row" style="gap: 30rpx;">
      <button class="button" style="flex: 1;" @tap="reset">重置</button>
    <button class="button" style="flex:2.5;" @tap="save">保存修改</button>
    </view>
  </view>
 <uni-popup
  ref="popup"
  type="bottom"
  background-color="#fff"
  borderRadius="10px 10px 0 0"
 >
  <view class="popup">
    <view style="display: flex; flex-direction: column; align-items: center;">
       <text>输入添加项并用，或。隔开</text>
       <text style="color: red; font-size: 12px;">温馨提示：空格和回车也可哟</text>
    </view>
    <textarea
      v-model="more"
      placeholder="请输入内容"
      maxlength="-1"
    />
    <button class="button" @tap="addMore">一键导入(共{{ num }}个选项)</button>
  </view>
 </uni-popup>
</template>

<script setup lang="ts">
import { useWheelStore } from '@/store/modules/wheel'
import Item from './components/Item.vue'
import MyInput from './components/MyInput.vue'
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'

const wheelStore = useWheelStore()
const popup = ref()

// 保存进入编辑页面时的数据
const backupWheel = ref({
  name: '',
  spinTime: 5,
  prizes: [] as string[],
})

// 页面加载时备份
onLoad(() => {
  backupWheel.value = JSON.parse(
    JSON.stringify({
      name: wheelStore.name,
      spinTime: wheelStore.spinTime,
      prizes: wheelStore.prizes,
    })
  )
})

  const more = ref('')

  const addPrize = (word: string ='') => {
      backupWheel.value.prizes.push(word)
  }
  const SonAddMore = (word: string, son: string[]) => {
    if (word.trim()) {
      son.push(word.trim())
    }
  }
 
  const num = computed(() => {
    return more.value.split(/[ ,，.。\n\r]+/).filter(item => item.trim()).length
  })
  const addMore = () => {
    const son: string[] = []
    let word = ''

    for (const item of more.value) {
      if (/[ ,，.。\n\r]/.test(item)) {
        SonAddMore(word, son)
        word = ''
      } else {
        word += item
      }
    }
    SonAddMore(word, son)
    backupWheel.value.prizes.push(...son)
    more.value = ''
  }


  const removePrize = (index: number) => {
    if (backupWheel.value.prizes.length <= 2) return
    backupWheel.value.prizes.splice(index, 1)
  }

  const reset = ()=>{
     backupWheel.value = {
    name: wheelStore.name,
    spinTime: wheelStore.spinTime,
    prizes: [...wheelStore.prizes]
  }
  more.value = ''
  }

const save = () => {
  wheelStore.addWheel(backupWheel.value)
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.wheel-edit {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx;
  background: #fff5e9;

  .prize-heading,
  .prize-row {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .prize-heading {
    width: 100%;
    justify-content: space-between;
  }

  .prize-row {
    margin-bottom: 16rpx;

    .prize-input {
      flex: 1;
    }
  }

  .action-row {
    width: 100%;
    margin-bottom: 16rpx;
  }

  .time-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    color: #999999;
    font-size: 35rpx;

    .time-label {
      flex: 1;
    }
  }

  .add-button {
    flex: none;
    margin: 0 0 0 16rpx;
  }

  .prefix-icon {
    width: 80rpx;
    height: 80rpx;
    margin: 0 12rpx 0 20rpx;
  }

  .delete-icon-disabled {
    opacity: 0.35;
  }

  .hint {
    display: block;
    margin-top: 20rpx;
    color: #999;
    font-size: 24rpx;
  }

  .save-button {
    margin-top: 32rpx;
    background: #1e5684;
    color: #fff;
  }

  // 穿透修改 uni-group 内部样式
  :deep(.uni-group__content) {
    padding: 0;
  }
}
.popup{
  width: 100vw;
  height: 60vh;
  padding: 40rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30rpx;
  textarea{
    width: 100%;
    height: 70%;
    background-color: #f5f5f5;
    border-radius: 10px;
    padding: 20rpx;
    box-sizing: border-box;
  }
  
}
.button{
    background-color: rgb(30, 86, 132);
    width: 100%;
    border-radius: 30px;
    color: #fff;
  }
</style>
