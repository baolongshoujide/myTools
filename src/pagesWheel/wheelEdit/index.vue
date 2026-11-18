<template>
  <view class="wheel-edit" :style="theme.pageStyle">
    <uni-forms ref="form" :model="draftWheel" :rules="formRules" err-show-type="toast">
      <Item>
        <template #title>轮盘标题</template>
        <uni-forms-item name="name">
          <MyInput v-model="draftWheel.name" placeholder="请输入轮盘名称" />
        </uni-forms-item>
      </Item>

      <Item>
        <uni-forms-item name="spinTime">
          <view class="time-row">
            <text class="time-label">旋转时间（秒）</text>
            <uni-number-box
              v-model="draftWheel.spinTime"
              :min="1"
              :max="9"
              :width="30"
            />
          </view>
        </uni-forms-item>
      </Item>

      <Item>
        <template #title>
          <view class="prize-heading">
            <text>奖品选项</text>
          </view>
        </template>
        <uni-forms-item name="prizes">
          <view v-for="(item, index) in draftWheel.prizes" :key="index" class="prize-row">
            <uni-forms-item :name="['prizes', index]" :rules="prizeRules" class="prize-input">
              <MyInput v-model="draftWheel.prizes[index]" :placeholder="`奖项${index + 1}`">
                <template #left>
                  <image
                    class="prefix-icon"
                    :class="{ 'delete-icon-disabled': draftWheel.prizes.length <= 2 }"
                    src="/static/delete.png"
                    mode="aspectFit"
                    @tap.stop="removeDraftPrize(index)"
                  />
                </template>
              </MyInput>
            </uni-forms-item>
          </view>
          <view class="action-row" @tap="addDraftPrize">
            <view class="action-display">
              <MyInput
                placeholder="添加新选项"
                :placeholder-style="`color:${theme.colors.accent};font-size:18px`"
                disabled
              >
                <template #left>
                  <image class="prefix-icon" src="/static/add.png" mode="aspectFit" />
                </template>
              </MyInput>
            </view>
          </view>
          <view class="action-row" @tap="openMore">
            <view class="action-display">
              <MyInput
                placeholder="批量添加选项"
                :placeholder-style="`color:${theme.colors.accent};font-size:18px`"
                disabled
              >
                <template #left>
                  <image class="prefix-icon" src="/static/bulk-add.png" mode="aspectFit" />
                </template>
              </MyInput>
            </view>
          </view>
        </uni-forms-item>
      </Item>
    </uni-forms>

    <text class="hint">至少保留两个奖项；保存后同步到转盘。</text>
    <view class="bottom-buttons">
      <button class="button reset" :disabled="saving" @tap="resetForm">重置</button>
      <button class="button save" :disabled="saving" :loading="saving" @tap="save">
        {{ isCreating ? '创建转盘' : '保存修改' }}
      </button>
    </view>
  </view>

  <uni-popup ref="popup" type="bottom" :background-color="theme.colors.surface" border-radius="10px 10px 0 0">
    <view class="popup" :style="theme.pageStyle">
      <view style="display: flex; flex-direction: column; align-items: center;">
        <text>输入添加项并用，或。隔开</text>
        <text class="bulk-hint">温馨提示：空格和回车也可哟</text>
      </view>
      <textarea v-model="more" placeholder="请输入内容" :maxlength="-1" />
      <button class="button" @tap="importDraftPrizes">一键导入(共{{ importedPrizes.length }}个选项)</button>
    </view>
  </uni-popup>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useWheelStore } from '@/store/modules/wheel'
import type { Wheel, WheelFormInstance, WheelPopupInstance } from '@/types/wheel'
import Item from './components/Item.vue'
import MyInput from './components/MyInput.vue'
import { usePageTheme } from '@/composables/usePageTheme'

const theme = usePageTheme()

const wheelStore = useWheelStore()
const form = ref<WheelFormInstance>()
const popup = ref<WheelPopupInstance>()
const isCreating = ref(false)
const saving = ref(false)
const more = ref('')
const draftWheel = ref<Wheel>({ id: '', name: '', spinTime: 5, prizes: ['', ''] })

const formRules = {
  name: {
    rules: [
      { required: true, errorMessage: '请输入转盘名称' },
      { pattern: '\\S', errorMessage: '转盘名称不能只有空格' },
    ],
  },
  spinTime: {
    rules: [
      { required: true, errorMessage: '请填写旋转时间' },
      { format: 'number', errorMessage: '旋转时间需为数字' },
      { minimum: 1, maximum: 9, errorMessage: '旋转时间需为1到9秒' },
    ],
  },
  prizes: {
    rules: [
      { required: true, errorMessage: '请添加奖项' },
      { format: 'array', errorMessage: '奖项格式不正确' },
      { minLength: 2, errorMessage: '至少保留两个奖项' },
    ],
  },
}

const prizeRules = [
  { required: true, errorMessage: '请填写每个奖项' },
  { pattern: '\\S', errorMessage: '奖项不能只有空格' },
]

const clearErrors = async () => {
  await nextTick()
  form.value?.clearValidate()
}

// 初始化和重置共用这一处；编辑时始终读取最初进入的那个转盘。
const resetForm = () => {
  if (isCreating.value) {
    draftWheel.value = { id: '', name: '', spinTime: 5, prizes: ['', ''] }
  } else {
    const item = wheelStore.wheels.find((item) => item.id === draftWheel.value.id)
    if (!item) {
      uni.showToast({ title: '转盘不存在，请返回重新选择', icon: 'none' })
      return
    }
    draftWheel.value = {
      id: item.id,
      name: item.name,
      spinTime: item.spinTime,
      prizes: item.prizes.slice(),
    }
  }
  more.value = ''
  clearErrors()
}

onLoad((options) => {
  isCreating.value = options?.mode === '1'
  draftWheel.value.id = isCreating.value ? '' : wheelStore.nowWheel.id
  resetForm()
  uni.setNavigationBarTitle({ title: isCreating.value ? '新建转盘' : '编辑转盘' })
})

const addDraftPrize = () => {
  draftWheel.value.prizes.push('')
}

const removeDraftPrize = (index: number) => {
  if (draftWheel.value.prizes.length <= 2) return
  draftWheel.value.prizes.splice(index, 1)
  clearErrors()
}

const importedPrizes = computed(() => {
  return more.value.split(/[\s,，.。]+/).filter((item) => item)
})

const openMore = () => {
  popup.value?.open()
}

const importDraftPrizes = () => {
  if (!importedPrizes.value.length) {
    uni.showToast({ title: '请先输入奖项', icon: 'none' })
    return
  }
  for (const item of importedPrizes.value) {
    const index = draftWheel.value.prizes.findIndex((item) => !item.trim())
    if (index === -1) {
      draftWheel.value.prizes.push(item)
    } else {
      draftWheel.value.prizes[index] = item
    }
  }
  more.value = ''
  popup.value?.close()
  clearErrors()
}

const save = async () => {
  if (saving.value || !form.value) return
  saving.value = true
  try {
    await nextTick()
    await form.value.validate()
    if (wheelStore.hasWheelName(draftWheel.value.name, isCreating.value ? undefined : draftWheel.value.id)) {
      uni.showToast({ title: '转盘名称已存在，请换一个', icon: 'none' })
      return
    }
    const saved = isCreating.value
      ? wheelStore.addWheel(draftWheel.value)
      : wheelStore.updateWheel(draftWheel.value)
    if (!saved) {
      uni.showToast({ title: '保存失败，转盘可能已不存在', icon: 'none' })
      return
    }
    uni.navigateBack()
  } catch {
    // 表单校验失败时，由 uni-forms 显示具体提示，并留在编辑页。
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.wheel-edit {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx;
  background: var(--dragon-page);
  padding-bottom: 140rpx;
  :deep(.uni-forms-item) {
    margin-bottom: 0;
  }
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

  .action-display {
    pointer-events: none;
  }

  .time-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    color: var(--dragon-muted);
    font-size: 35rpx;

    .time-label {
      flex: 1;
    }
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
    color: var(--dragon-muted);
    font-size: 24rpx;
  }
  .bottom-buttons {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  display: flex;
  gap: 30rpx;
  padding: 20rpx 30rpx;
  box-sizing: border-box;
  background-color: var(--dragon-base);
  z-index: 99;

  .button {
    margin: 0;
  }

  .reset {
    flex: 1;
    background-color: #563247;
  }

  .save {
    flex: 2.5;
  }
}
  // 穿透修改 uni-group 内部样式
  :deep(.uni-group__content) {
    padding: 0;
  }
}
.popup{
  .bulk-hint {
    color: var(--dragon-muted);
    font-size: 12px;
  }

  width: 100vw;
  height: 60vh;
  padding: 40rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30rpx;
  textarea{
    color: var(--dragon-text);
    width: 100%;
    height: 70%;
    background-color: var(--dragon-raised);
    border-radius: 10px;
    padding: 20rpx;
    box-sizing: border-box;
  }
  
}
.button{
    background-color: var(--dragon-primary);
    width: 100%;
    border-radius: 30px;
    color: #fff;
  }
</style>
