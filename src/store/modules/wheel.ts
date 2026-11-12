import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useWheelStore = defineStore('wheel', () => {
  const name = ref('我的转盘')
  const spinTime = ref(5)
  const prizes = ref([
    '一等奖',
    '二等奖',
    '三等奖',
    '谢谢参与',
    '幸运奖',
    '再来一次',
  ])
  

  

  const addWheel = (data: { name: string; spinTime: number; prizes: string[] }) => {
    name.value = data.name
    spinTime.value = data.spinTime
    prizes.value = [...data.prizes]
  }

  return {
    name,
    spinTime,
    prizes,
    addWheel,
  }
})
