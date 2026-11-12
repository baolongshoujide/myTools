<template>
  <view class="input-box">
    <uni-easyinput
      v-bind="$attrs"
      :model-value="props.modelValue"
      :input-border="false"
      :styles="inputStyles"
      :placeholder-style="props.placeholderStyle"
      @update:model-value="onUpdateModelValue"
    >
      <template #left>
        <slot name="left" />
      </template>
    </uni-easyinput>
  </view>
</template>

<script setup lang="ts">
defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<{
  modelValue?: string | number | null
  placeholderStyle?: string
}>(), {
  placeholderStyle: 'font-size: 18px;',
})

const emit = defineEmits<{
  (event: 'update:modelValue', value: string | number): void
}>()

const onUpdateModelValue = (value: string | number) => {
  emit('update:modelValue', value)
}

const inputStyles = {
  color: '#333333',
  backgroundColor: '#f5f5f5',
  borderColor: '#f5f5f5',
}
</script>

<style lang="scss" scoped>
.input-box {
  height: 80rpx;
  padding: 0;
  margin: 0;
  border-radius: 50rpx;
  overflow: hidden;
  background-color: #f5f5f5;
  
}
</style>
