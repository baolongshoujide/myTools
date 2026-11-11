<template>
  <view class="wheelSetting">
    <uni-forms
      ref="form"
      label-position="top"
    >
      <uni-forms-item
        required
        label="轮盘名称"
        name=""
      >
        <uni-easyinput
          v-model="forms.name"
          type="text"
          @confirm=""
        />
      </uni-forms-item>
      <button @click="">提交</button>
      <button @click="">重置</button>
    </uni-forms>

  </view>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const forms = ref({
  name:''
})
</script>

<style scoped></style>