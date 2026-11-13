import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { Wheel } from '@/types/wheel'

export const useWheelStore = defineStore('wheel', () => {
  const wheels = ref<Wheel[]>([
    {
      id: '1',
      name: '我的转盘',
      spinTime: 5,
      prizes: ['一等奖', '二等奖', '三等奖', '谢谢参与', '幸运奖', '再来一次'],
    },
  ])

  const currentWheelId = ref('1')
  const currentWheel = computed(
    () => wheels.value.find((item) => item.id === currentWheelId.value) ?? wheels.value[0]
  )

  const updateWheel = (data: Wheel) => {
    const index = wheels.value.findIndex((item) => item.id === data.id)
    if (index === -1) return

    wheels.value[index] = {
      id: data.id,
      name: data.name,
      spinTime: data.spinTime,
      prizes: data.prizes.slice(),
    }
  }

  return {
    wheels,
    currentWheelId,
    currentWheel,
    updateWheel,
  }
})
