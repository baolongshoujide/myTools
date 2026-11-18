<template>
  <view class="clicker-panel">
    <!-- #ifdef MP-WEIXIN -->
    <uni-notice-bar
      text="微信小程序可创建和保存方案，执行连点或滑动需使用 Android 版龙核工具箱。"
      :show-icon="true"
      :scrollable="true"
      :color="theme.colors.accent"
      :background-color="theme.colors.raised"
    />
    <!-- #endif -->
    <view v-if="draft" key="editor">
      <view class="card">
        <text class="title">{{ draft.id ? '编辑方案' : '新建方案' }}</text>
        <text class="label">方案名称</text>
        <input v-model="draft.name" class="input" maxlength="24" placeholder="例如：快速连点" />
        <text class="label">首个标记类型</text>
        <view class="actions">
          <button class="button" :class="{ primary: draft.action === 'tap' }" @tap="selectAction('tap')">连续点击</button>
          <button class="button" :class="{ primary: draft.action === 'swipe' }" @tap="selectAction('swipe')">重复滑动</button>
        </view>
        <text class="label">操作间隔（毫秒）</text>
        <input v-model.number="draft.interval" class="input" type="number" />
        <text class="label">执行轮数（每轮按编号执行一遍）</text>
        <input v-model.number="draft.count" class="input" type="number" />
        <template v-if="hasSwipe(draft)">
          <text class="label">单次滑动时长（毫秒）</text>
          <input v-model.number="draft.swipeDuration" class="input" type="number" />
        </template>
        <view v-if="isAndroidApp" class="position-tools">
          <button class="button" @tap="locateDraft">在其他 App 添加或拖动标记</button>
          <text class="hint">已配置 {{ draft.points?.length || 0 }} 组位置。点按钮后切到目标 App 即可定位。</text>
        </view>
        <view class="actions form-actions">
          <button class="button" @tap="closeEditor">取消</button>
          <button class="button primary" @tap="savePlan">保存方案</button>
        </view>
        <text v-if="saveError" class="hint save-error">{{ saveError }}</text>
      </view>
    </view>

    <view v-else key="list">
      <!-- #ifndef MP-WEIXIN -->
      <text class="hint">{{ isAndroidApp ? '点「使用」打开悬浮面板，再切到目标页面开始。' : '执行时请打开 Android App。' }}</text>
      <!-- #endif -->
      <button v-if="isAndroidApp" class="button import-button" @tap="importPlan">从剪贴板导入方案</button>
      <view v-if="!plans.length" class="card empty">暂无方案，点击底部加号新建。</view>
      <view v-for="item in plans" :key="item.id" class="card">
        <text class="plan-name">{{ item.name }}</text>
        <text class="hint">{{ describeActions(item) }} · 间隔 {{ item.interval }} ms · {{ item.count }} 轮</text>
        <text v-if="hasSwipe(item)" class="hint">单次滑动 {{ item.swipeDuration }} ms</text>
        <view class="actions form-actions">
          <!-- #ifdef MP-WEIXIN -->
          <button
            v-if="canLaunchApp"
            class="button primary"
            open-type="launchApp"
            :app-parameter="appParameter(item)"
            @error="showAppPrompt(item)"
          >使用</button>
          <button v-else class="button primary" @tap="showAppPrompt(item)">使用</button>
          <!-- #endif -->
          <!-- #ifndef MP-WEIXIN -->
          <button class="button primary" @tap="usePlan(item)">使用</button>
          <!-- #endif -->
          <button class="button" @tap="editPlan(item)">编辑</button>
          <button class="button danger" @tap="deletePlan(item)">删除</button>
        </view>
        <button v-if="!isAndroidApp" class="button import-button" @tap="copyPlan(item)">复制方案到 App</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import type { ClickerLocation, ClickerPlan } from '@/types/clicker'
import { useThemeStore } from '@/store/modules/theme'
// #ifdef APP-PLUS
import { isClickerReady, openClickerSettings, configureClicker, drainClickerChanges } from '@/uni_modules/mytools-clicker'
// #endif

const theme = useThemeStore()

const storageKey = 'mytools-clicker-plans'
const plans = ref<ClickerPlan[]>([])
const draft = ref<ClickerPlan | null>(null)
const saveError = ref('')
const defaultCoordinates = { x: 50, y: 65, endX: 50, endY: 35 }
const hasSwipe = (item: ClickerPlan) =>
  item.points?.length ? item.points.some((point) => (point.action ?? item.action) === 'swipe') : item.action === 'swipe'

const describeActions = (item: ClickerPlan) => {
  if (!item.points?.length) return item.action === 'tap' ? '连续点击' : '重复滑动'
  const swipeCount = item.points.filter((point) => (point.action ?? item.action) === 'swipe').length
  const tapCount = item.points.length - swipeCount
  return [tapCount ? tapCount + ' 个点击' : '', swipeCount ? swipeCount + ' 组滑动' : ''].filter(Boolean).join('、')
}
let isAndroidApp = false
// #ifdef APP-PLUS
isAndroidApp = plus.os.name === 'Android'
// #endif
// #ifdef MP-WEIXIN
const canLaunchApp = ref(false)

const appParameter = (item: ClickerPlan) => JSON.stringify({ type: 'clicker-plan', plan: item })
// #endif

try {
  const stored = uni.getStorageSync(storageKey)
  if (Array.isArray(stored)) plans.value = stored
} catch {
  uni.showToast({ title: '读取方案失败', icon: 'none' })
}

const createPlan = () => {
  if (draft.value) return
  saveError.value = ''
  draft.value = { id: '', name: '', action: 'tap', interval: 300, count: 10, swipeDuration: 300, ...defaultCoordinates }
  if (isAndroidApp) locateDraft()
}

const editPlan = (item: ClickerPlan) => {
  saveError.value = ''
  draft.value = { ...defaultCoordinates, ...item }
}

const selectAction = (action: ClickerPlan['action']) => {
  if (draft.value) draft.value.action = action
}

const closeEditor = () => {
  saveError.value = ''
  draft.value = null
}

const validCoordinate = (value: unknown): value is number =>
  typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 100

const hasPlanName = (items: ClickerPlan[], name: string, exceptId?: string) => {
  const normalized = name.trim().toLowerCase()
  return items.some((item) => item.id !== exceptId && item.name.trim().toLowerCase() === normalized)
}

const savePlans = (items: ClickerPlan[]) => {
  try {
    uni.setStorageSync(storageKey, items)
    plans.value = items
    return true
  } catch {
    uni.showToast({ title: '无法保存方案，请重试', icon: 'none' })
    return false
  }
}

const savePlan = () => {
  saveError.value = ''
  // #ifdef APP-PLUS
  syncPositions()
  // #endif
  const item = draft.value
  if (!item) return
  const name = item.name.trim()
  const interval = Number(item.interval)
  const count = Number(item.count)
  const swipeDuration = Number(item.swipeDuration)
  const coordinates = {
    x: item.x ?? defaultCoordinates.x,
    y: item.y ?? defaultCoordinates.y,
    endX: item.endX ?? defaultCoordinates.endX,
    endY: item.endY ?? defaultCoordinates.endY,
  }
  let error = ''
  if (!name) error = '请输入方案名称'
  else if (hasPlanName(plans.value, name, item.id)) error = '方案名称已存在，请换一个'
  else if (!Number.isSafeInteger(interval) || interval < 1 || interval > 60000) error = '操作间隔应为 1 到 60000 毫秒'
  else if (!Number.isSafeInteger(count) || count < 1 || count > 10000) error = '重复次数应为 1 到 10000'
  else if (hasSwipe(item) && (!Number.isSafeInteger(swipeDuration) || swipeDuration < 1 || swipeDuration > 10000)) error = '滑动时长应为 1 到 10000 毫秒'
  else if (!Object.values(coordinates).every(validCoordinate)) error = '请重新拖动操作位置'
  if (error) {
    saveError.value = error
    return
  }

  const id = item.id || Date.now() + '-' + Math.random().toString(36).slice(2, 8)
  const updated: ClickerPlan = { id, name, action: item.action, interval, count, swipeDuration: hasSwipe(item) ? swipeDuration : 300, ...coordinates, points: item.points }
  const items = item.id
    ? plans.value.map((plan) => plan.id === id ? updated : plan)
    : [updated, ...plans.value]
  if (savePlans(items)) {
    closeEditor()
    uni.showToast({ title: '方案已保存' })
  } else {
    saveError.value = '方案未能写入本地，请重试'
  }
}

const deletePlan = (item: ClickerPlan) => {
  uni.showModal({
    title: '删除方案',
    content: '确定删除「' + item.name + '」？',
    confirmText: '删除',
    success: ({ confirm }) => {
      if (confirm) savePlans(plans.value.filter((plan) => plan.id !== item.id))
    },
  })
}

const importPlan = () => {
  uni.getClipboardData({
    success: ({ data }) => {
      try {
        const payload = JSON.parse(data)
        const item = payload.plan
        if (payload.type !== 'clicker-plan' || typeof item?.name !== 'string' || !['tap', 'swipe'].includes(item.action)) throw new Error()
        draft.value = {
          ...defaultCoordinates, id: '', name: item.name.trim().slice(0, 24), action: item.action,
          interval: Number(item.interval), count: Number(item.count), swipeDuration: Number(item.swipeDuration ?? 300),
          points: normalizePoints(item.points),
          x: validCoordinate(item.x) ? item.x : defaultCoordinates.x,
          y: validCoordinate(item.y) ? item.y : defaultCoordinates.y,
          endX: validCoordinate(item.endX) ? item.endX : defaultCoordinates.endX,
          endY: validCoordinate(item.endY) ? item.endY : defaultCoordinates.endY,
        }
      } catch {
        uni.showToast({ title: '剪贴板里没有可导入的方案', icon: 'none' })
      }
    },
    fail: () => uni.showToast({ title: '无法读取剪贴板', icon: 'none' }),
  })
}

const normalizePoints = (value: unknown): ClickerLocation[] | undefined => {
  if (!Array.isArray(value)) return undefined
  return value.filter((point) => point && [point.x, point.y, point.endX, point.endY].every(validCoordinate))
    .slice(0, 20)
    .map(({ action, duration, x, y, endX, endY }) => ({
      action: action === 'tap' || action === 'swipe' ? action : undefined, x, y, endX, endY,
      duration: Number.isInteger(duration) && duration >= 1 && duration <= 10000 ? duration : undefined,
    }))
}

// #ifdef APP-PLUS
const draftPositionId = '__draft__'
let pendingClickerAction: (() => void) | null = null
let permissionTimer: ReturnType<typeof setTimeout> | undefined

const showNativeError = (error: unknown) => {
  console.warn('连点器原生调用失败', error)
  uni.showModal({
    title: '无法打开连点器浮窗',
    content: '请确认当前使用的是包含连点器插件的新版 Android 自定义基座。',
    showCancel: false,
  })
}

const runWithClicker = (action: () => void) => {
  try {
    if (isClickerReady()) {
      action()
      return
    }
    uni.showModal({
      title: '开启连点器服务',
      content: '在系统无障碍设置中启用「myTools 连点器」，再返回本页。',
      confirmText: '去设置',
      success: ({ confirm }) => {
        if (!confirm) return
        pendingClickerAction = action
        try {
          openClickerSettings()
        } catch (error) {
          pendingClickerAction = null
          showNativeError(error)
        }
      },
    })
  } catch (error) {
    showNativeError(error)
  }
}

const resumeClicker = (attempt = 0) => {
  if (!pendingClickerAction) return
  try {
    if (isClickerReady()) {
      const action = pendingClickerAction
      pendingClickerAction = null
      action()
    } else if (attempt < 8) {
      permissionTimer = setTimeout(() => resumeClicker(attempt + 1), 250)
    } else {
      pendingClickerAction = null
      uni.showModal({
        title: '连点器服务还未连接',
        content: '请确认无障碍设置里已开启「myTools 连点器」。如果列表里没有这一项，请换用新版 Android 自定义基座。',
        showCancel: false,
      })
    }
  } catch (error) {
    pendingClickerAction = null
    showNativeError(error)
  }
}

const syncPositions = () => {
  if (!isAndroidApp) return
  let changes: ClickerPlan[]
  try {
    changes = JSON.parse(drainClickerChanges())
  } catch (error) {
    // 原生基座不匹配时，仍然允许保存方案的名称和参数。
    console.warn('读取悬浮窗点位失败', error)
    return
  }
  if (!Array.isArray(changes) || !changes.length) return
  const items = plans.value.slice()
  let changed = false
  for (const item of changes) {
    const points = normalizePoints(item.points)
    if (!points?.length) continue
    if (item.id === draftPositionId) {
      if (draft.value) draft.value.points = points
      continue
    }
    const index = items.findIndex((entry) => entry.id === item.id)
    if (index < 0) {
      const baseName = item.name.trim().slice(0, 24) || '新方案'
      let name = baseName
      let number = 2
      while (hasPlanName(items, name)) {
        const suffix = ' ' + number++
        name = baseName.slice(0, 24 - suffix.length) + suffix
      }
      items.unshift({ ...item, name, points })
    } else {
      items[index] = { ...items[index], points }
    }
    changed = true
  }
  if (changed) savePlans(items)
}

const onClickerForeground = () => {
  syncPositions()
  clearTimeout(permissionTimer)
  resumeClicker()
}

onMounted(() => {
  if (isAndroidApp) uni.onAppShow?.(onClickerForeground)
})
onUnmounted(() => {
  pendingClickerAction = null
  clearTimeout(permissionTimer)
  if (isAndroidApp) uni.offAppShow?.(onClickerForeground)
})
// #endif

const locateDraft = () => {
  // #ifdef APP-PLUS
  const item = draft.value
  if (!item || !isAndroidApp) return
  runWithClicker(() => {
    if (draft.value === item) openDraftOverlay()
  })
  // #endif
}

// #ifdef APP-PLUS
const openDraftOverlay = () => {
  const item = draft.value
  if (!item) return
  const plan = {
    ...defaultCoordinates, ...item,
    id: draftPositionId, name: item.name.trim() || '未命名方案',
    interval: Number(item.interval) || 300, count: Number(item.count) || 10,
    swipeDuration: Number(item.swipeDuration) || 300,
  }
  if (!configureClicker(JSON.stringify([plan, ...plans.value]), draftPositionId, true)) {
    uni.showToast({ title: '无法打开浮窗，请检查方案参数', icon: 'none' })
    return
  }
  uni.showToast({ title: '拖动定位，长按标记可设动作', icon: 'none' })
}
// #endif

const usePlan = (item: ClickerPlan) => {
  // #ifdef APP-PLUS
  if (isAndroidApp) {
    runWithClicker(() => {
      if (!configureClicker(JSON.stringify(plans.value), item.id, !item.points?.length)) {
        uni.showToast({ title: '无法打开浮窗，请检查方案参数', icon: 'none' })
      }
    })
    return
  }
  // #endif
  showAppPrompt(item)
}

const showAppPrompt = (item?: ClickerPlan) => {
  uni.showModal({
    title: '请前往 Android App 使用',
    content: item ? '可复制此方案，再打开 myTools Android App，从连点器页导入。' : '请打开 myTools Android App，在连点器页创建或导入方案。',
    showCancel: Boolean(item),
    confirmText: item ? '复制方案' : '知道了',
    success: ({ confirm }) => {
      if (confirm && item) copyPlan(item)
    },
  })
}

const copyPlan = (item: ClickerPlan) => {
  uni.setClipboardData({
    data: JSON.stringify({ type: 'clicker-plan', plan: item }),
    fail: () => uni.showToast({ title: '复制失败，请重试', icon: 'none' }),
  })
}

const refresh = () => {
  // #ifdef MP-WEIXIN
  const scene = uni.getEnterOptionsSync()?.scene
  canLaunchApp.value = scene === 1036 || scene === 1069
  // #endif
  // #ifdef APP-PLUS
  onClickerForeground()
  // #endif
}

onMounted(refresh)
defineExpose({ createPlan, refresh })
</script>

<style lang="scss" scoped>
.clicker-panel {
  color: var(--dragon-text);

  .actions {
    display: flex;
    align-items: center;
    gap: 16rpx;
  }

  .title,
  .plan-name {
    font-weight: 600;
  }

  .title { font-size: 36rpx; }
  .plan-name { font-size: 32rpx; }

  .hint {
    display: block;
    margin-top: 12rpx;
    color: var(--dragon-muted);
    font-size: 25rpx;
  }

  .card {
    margin-top: 24rpx;
    padding: 28rpx;
    border: 1rpx solid var(--dragon-border);
    border-radius: 24rpx;
    background: var(--dragon-surface);

    .label {
      display: block;
      margin: 24rpx 0 12rpx;
      color: var(--dragon-muted);
      font-size: 26rpx;
    }

    .input {
      height: 80rpx;
      padding: 0 20rpx;
      border-radius: 14rpx;
      background: var(--dragon-raised);
      color: var(--dragon-text);
    }
  }

  .empty { color: var(--dragon-muted); }

  .form-actions { margin-top: 24rpx; }

  .save-error { color: var(--dragon-danger); }

  .position-tools {
    margin-top: 24rpx;
  }

  .button {
    flex: 1;
    margin: 0;
    padding: 0 14rpx;
    border-radius: 14rpx;
    background: var(--dragon-raised);
    color: var(--dragon-muted);
    font-size: 26rpx;

    &::after { border: none; }
    &.primary { background: var(--dragon-primary); color: #fff; }
    &.danger { color: var(--dragon-danger); }
    &.import-button { margin-top: 20rpx; }
  }
}
</style>
