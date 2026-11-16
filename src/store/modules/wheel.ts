import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { Wheel, WheelDraft,Settings } from '@/types/wheel'

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
      name: '一周转盘1',
      spinTime: 5,
      prizes: ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'],
    },
    {
      id: '3',
      name: '早餐转盘',
      spinTime: 5,
      prizes: ['包子', '油条', '豆浆', '煎饼', '面包', '鸡蛋', '牛奶', '馄饨', '粥', '饺子', '三明治', '面条'],
    },
     {
    id: '4',
    name: '周末玩什么',
    spinTime: 5,
    prizes: ['看电影', '逛街', '打游戏', '爬山', '唱歌', '旅游', '宅家', '运动'],
  },
  {
    id: '6',
    name: '学习任务',
    spinTime: 5,
    prizes: ['背单词', '学英语', '刷题', '看书', '练代码', '复习', '做笔记'],
  },
  {
    id: '7',
    name: '家务分配',
    spinTime: 5,
    prizes: ['语文','数学','英语','物理','化学','生物','历史','地理','政治',],
  },
  {
    id: '12',
    name: '要不要做',
    spinTime: 5,
    prizes: ['要', '不要',  '明天再说'],
  },
  {
    id: '13',
    name: '今天喝哪家',
    spinTime: 5,
    prizes: ['蜜雪冰城','甜啦啦','古茗','茶百道','沪上阿姨','霸王茶姬','一点点',
    ],
  },
  ])

  const settings = ref<Settings>({
    dong: false,
    noRepeat: false,
    showModal: false,
})

  const nowWheelId = ref('1')
  const nowWheel = computed(
    () => wheels.value.find((item) => item.id === nowWheelId.value) ?? wheels.value[0]
  )

  const copyWheel = (data: WheelDraft, id: string): Wheel => {
    return {
      id,
      name: data.name.trim(),
      spinTime: data.spinTime,
      prizes: data.prizes.map((item) => item.trim()),
    }
  }

  const updateWheel = (data: Wheel) => {
    const index = wheels.value.findIndex((item) => item.id === data.id)
    if (index === -1) return false
    wheels.value[index] = copyWheel(data, data.id)
    return true
  }

  const selectWheel = (id:string)=>{
    if (!wheels.value.some((item) => item.id === id)) return false
    nowWheelId.value = id
    return true
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
    wheels.value.push(copyWheel(data, id))
    nowWheelId.value = id
    return true
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
    settings,
    updateWheel,
    selectWheel,
    addPrize,
    addWheel,
    removePrize,
  }
}, {
  persist: {
    key: 'mytools-wheel',
    pick: ['wheels', 'nowWheelId','settings'],
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
