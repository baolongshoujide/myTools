import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { Wheel, WheelDraft } from '@/types/wheel'

export const useWheelStore = defineStore('wheel', () => {
  const wheels = ref<Wheel[]>([
    {
      id: '1',
      name: '我的转盘',
      spinTime: 5,
      prizes: ['一等奖', '二等奖', '三等奖', '谢谢参与', '幸运奖', '再来一次'],
    },
    {
      id: '2',
      name: '一周转盘',
      spinTime: 5,
      prizes: ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'],
    },
    {
      id: '3',
      name: '一周转盘',
      spinTime: 5,
      prizes: ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'],
    },
  ])

  const nowWheelId = ref('1')
  const nowWheel = computed(
    () => wheels.value.find((item) => item.id === nowWheelId.value) ?? wheels.value[0]
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

  const selectWheel = (id:string)=>{
    nowWheelId.value = id
  }

  const addPrize = (id: string, name: string) => {
    const item = wheels.value.find((item) => item.id === id)
    if (!item || !name.trim()) return false
    const prizes = item.prizes.slice()
    prizes.push(name.trim())
    item.prizes = prizes
    return true
  }

  const addWheel = (data: WheelDraft) => {
    let id = ''
    do {
      id = 'wheel-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8)
    } while (wheels.value.some((item) => item.id === id))
    wheels.value.push({
      id,
      name: data.name,
      spinTime: data.spinTime,
      prizes: data.prizes.slice(),
    })
    nowWheelId.value = id
  }

  const removePrize = (id: string, prizeIndex: number) => {
    const item = wheels.value.find((item) => item.id === id)
    if (!item || item.prizes.length <= 2 || !Number.isInteger(prizeIndex) || prizeIndex < 0 || prizeIndex >= item.prizes.length) return false
    const prizes = item.prizes.slice()
    prizes.splice(prizeIndex, 1)
    item.prizes = prizes
    return true
  }

  return {
    wheels,
    nowWheelId,
    nowWheel,
    updateWheel,
    selectWheel,
    addPrize,
    addWheel,
    removePrize,
  }
}, {
  persist: {
    key: 'mytools-wheel',
    pick: ['wheels', 'nowWheelId'],
    storage: {
      getItem: (key) => {
        const data = uni.getStorageSync(key)
        return typeof data === 'string' ? data : null
      },
      setItem: (key, value) => {
        uni.setStorageSync(key, value)
      },
    },
  },
})
