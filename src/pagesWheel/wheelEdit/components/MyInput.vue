<template>
  <view class="input-box">
    <uni-easyinput
      v-bind="$attrs"
      :model-value="props.modelValue"
      :input-border="false"
      :styles="inputStyles"
      :placeholder-style="props.placeholderStyle || defaultPlaceholderStyle"
      @update:model-value="onUpdateModelValue"
    >
      <template #left>
        <slot name="left" />
      </template>
    </uni-easyinput>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/store/modules/theme'
import type { WheelInputEmits, WheelInputProps, WheelInputValue } from '@/types/wheel'

defineOptions({ inheritAttrs: false })

const props = defineProps<WheelInputProps>()
const theme = useThemeStore()
const defaultPlaceholderStyle = computed(() => 'font-size: 18px; color: ' + theme.colors.muted + ';')

const emit = defineEmits<WheelInputEmits>()

const onUpdateModelValue = (value: WheelInputValue) => {
  emit('update:modelValue', value)
}

const inputStyles = computed(() => ({
  color: theme.colors.text,
  backgroundColor: theme.colors.raised,
  borderColor: theme.colors.raised,
}))
</script>

<style lang="scss" scoped>
.input-box {
  height: 80rpx;
  padding: 0;
  margin: 0;
  border-radius: 50rpx;
  overflow: hidden;
  background-color: var(--dragon-raised);
  
}
</style>
