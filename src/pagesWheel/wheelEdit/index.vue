<template>
  <view class="wheel-edit">
    <Item>
      <template #title>轮盘标题</template>
      <MyInput v-model="wheelStore.name" placeholder="请输入轮盘名称" />
    </Item>

    <Item>
      <template #title>旋转时间（秒）</template>
      <MyInput
        v-model.number="wheelStore.spinTime"
        type="number"
        placeholder="请输入旋转秒数"
      />
    </Item>

    <Item>
      <template #title>
        <view class="prize-heading">
          <text>奖品选项</text>
          <button class="add-button" size="mini" @tap="wheelStore.addPrize">
            添加奖项
          </button>
        </view>
      </template>

      <view
        v-for="(prize, index) in wheelStore.prizes"
        :key="index"
        class="prize-row"
      >
        <MyInput
          v-model="wheelStore.prizes[index]"
          class="prize-input"
          :placeholder="`奖项${index + 1}`"
        >
          <template #left>
            <image
              class="delete-icon"
              :class="{ 'delete-icon-disabled': wheelStore.prizes.length <= 2 }"
              src="/static/delete.png"
              mode="aspectFit"
              @tap.stop="wheelStore.prizes.length > 2 && wheelStore.removePrize(index)"
            />
          </template>
        </MyInput>
      </view>
    </Item>

    <text class="hint">至少保留两个奖项；编辑内容会立即同步到转盘。</text>
  </view>
</template>

<script setup lang="ts">
import { useWheelStore } from '@/store/modules/wheel'
import Item from './components/Item.vue'
import MyInput from './components/MyInput.vue'

const wheelStore = useWheelStore()
</script>

<style lang="scss" scoped>
.wheel-edit {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx;
  background: #fff5e9;
}

.prize-heading,
.prize-row {
  display: flex;
  align-items: center;
}

.prize-heading {
  width: 100%;
  justify-content: space-between;
}

.prize-row {
  margin-bottom: 16rpx;
}

.prize-input {
  flex: 1;
}

.add-button {
  flex: none;
  margin: 0 0 0 16rpx;
}

.delete-icon {
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
</style>
