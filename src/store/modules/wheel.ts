import { defineStore } from 'pinia'
import { ref } from 'vue'

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

  const addPrize = () => {
    prizes.value.push(`奖项${prizes.value.length + 1}`)
  }

  const removePrize = (index: number) => {
    if (prizes.value.length <= 2) return
    prizes.value.splice(index, 1)
  }

  return {
    name,
    spinTime,
    prizes,
    addPrize,
    removePrize,
  }
})
