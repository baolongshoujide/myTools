<template>
  <view class="my-page">
    <view class="profile-card" hover-class="profile-card-pressed" @tap="openLogin">
      <view class="profile-main">
        <view class="avatar"><image class="avatar-image" src="/static/Lhlogo.jpg" mode="aspectFill" /></view>
        <view class="profile-info">
          <text class="profile-name">点击登录</text>
          <text class="profile-description">开启你的个人工具空间</text>
        </view>
        <uni-icons type="arrow-right" :size="20" :color="theme.colors.accent" />
      </view>
    </view>

    <view class="section-heading">
      <text class="section-title">我的工具箱</text>
      <text class="section-note">让常用的工具，随手可及</text>
    </view>
    <view class="shortcuts">
      <view class="shortcut-card">
        <view class="shortcut-icon wheel-icon"><uni-icons type="refresh" :size="28" :color="theme.colors.accent" /></view>
        <text class="shortcut-title">我的转盘</text>
        <text class="shortcut-description">收藏每一个好选择</text>
        <view class="shortcut-link">查看转盘 <uni-icons type="arrow-right" :size="12" :color="theme.colors.muted" /></view>
      </view>
      <view class="shortcut-card">
        <view class="shortcut-icon image-icon"><uni-icons type="image" :size="28" :color="theme.colors.accent" /></view>
        <text class="shortcut-title">图片去水印</text>
        <text class="shortcut-description">让画面清爽一点</text>
        <view class="shortcut-link">开始处理 <uni-icons type="arrow-right" :size="12" :color="theme.colors.muted" /></view>
      </view>
    </view>

    <view class="section-heading"><text class="section-title">更多</text></view>
    <view class="menu-card">
      <view class="menu-item" @tap="openRecycleBin">
        <view class="menu-icon"><uni-icons type="trash" :size="22" :color="theme.colors.accent" /></view>
        <text class="menu-title">转盘回收站</text>
        <text class="menu-note">保留7天</text>
        <uni-icons type="arrow-right" :size="16" :color="theme.colors.muted" />
      </view>
      <view class="menu-item" @tap="settingsOpen = !settingsOpen">
        <view class="menu-icon"><uni-icons type="gear" :size="22" :color="theme.colors.accent" /></view>
        <text class="menu-title">通用设置</text>
        <text class="menu-note">{{ theme.mode === 'light' ? '浅色' : '深色' }}</text>
        <uni-icons :type="settingsOpen ? 'arrow-down' : 'arrow-right'" :size="16" :color="theme.colors.muted" />
      </view>
      <view v-if="settingsOpen" class="theme-settings">
        <text class="theme-label">外观主题</text>
        <view class="theme-options">
          <button
            class="theme-option"
            :class="{ selected: theme.mode === 'light' }"
            @tap="theme.setMode('light')"
          >浅色</button>
          <button
            class="theme-option"
            :class="{ selected: theme.mode === 'dark' }"
            @tap="theme.setMode('dark')"
          >深色</button>
        </view>
      </view>
      <view class="menu-item">
        <view class="menu-icon"><uni-icons type="chatbubble" :size="22" :color="theme.colors.accent" /></view>
        <text class="menu-title">意见反馈</text>
        <uni-icons type="arrow-right" :size="16" :color="theme.colors.muted" />
      </view>
      <view class="menu-item">
        <view class="menu-icon"><uni-icons type="info" :size="22" :color="theme.colors.accent" /></view>
        <text class="menu-title">关于 myTools</text>
        <text class="menu-note">让小事，更简单</text>
        <uni-icons type="arrow-right" :size="16" :color="theme.colors.muted" />
      </view>
    </view>
    <view class="page-footer">
      <text class="footer-name">myTools</text>
      <text class="footer-description">属于你的口袋工具箱</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useThemeStore } from '@/store/modules/theme'

const theme = useThemeStore()
const settingsOpen = ref(false)
const openLogin = () => {
  uni.showToast({ title: '登录功能即将开放', icon: 'none' })
}
const openRecycleBin = () => {
  uni.navigateTo({ url: '/pages/my/recycle' })
}
</script>

<style lang="scss" scoped>
.my-page {
  padding-top: 42rpx;
  color: var(--dragon-text);

  .page-heading {
    display: flex;
    flex-direction: column;
    padding: 0 8rpx 32rpx;

    .eyebrow {
      color: var(--dragon-muted);
      font-size: 22rpx;
      letter-spacing: 4rpx;
    }
    .page-title {
      margin-top: 12rpx;
      font-size: 44rpx;
      font-weight: 700;
    }
    .page-description {
      margin-top: 16rpx;
      color: var(--dragon-muted);
      font-size: 25rpx;
      line-height: 1.6;
    }
  }

  .profile-card {
    padding: 36rpx 28rpx;
    border: 2rpx solid var(--dragon-border);
    border-radius: 28rpx;
    background: var(--dragon-surface);
    transition: transform 0.15s ease;

    .profile-main {
      display: flex;
      align-items: center;

      .avatar {
        overflow: hidden;
        display: flex;
        flex-shrink: 0;
        align-items: center;
        justify-content: center;
        width: 112rpx;
        height: 112rpx;
        border: 6rpx solid #ffffff;
        border-radius: 50%;
        background: linear-gradient(140deg, #83b2ff, #6585e8);
        box-sizing: border-box;

        .avatar-image {
          display: block;
          width: 100%;
          height: 100%;
        }
      }
      .profile-info {
        display: flex;
        flex: 1;
        min-width: 0;
        flex-direction: column;
        margin-left: 24rpx;

        .profile-name {
          font-size: 36rpx;
          font-weight: 600;
          line-height: 1.5;
        }
        .profile-description {
          margin-top: 10rpx;
          color: var(--dragon-muted);
          font-size: 23rpx;
          line-height: 1.6;
        }
      }
    }
  }

  .profile-card-pressed {
    transform: scale(0.98);
  }

  .section-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 40rpx 8rpx 22rpx;

    .section-title {
      font-size: 31rpx;
      font-weight: 600;
    }
    .section-note {
      color: var(--dragon-muted);
      font-size: 22rpx;
    }
  }

  .shortcuts {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20rpx;

    .shortcut-card {
      display: flex;
      flex-direction: column;
      padding: 28rpx;
      border-radius: 24rpx;
      background: var(--dragon-surface);

      .shortcut-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 80rpx;
        height: 80rpx;
        margin-bottom: 22rpx;
        border-radius: 24rpx;

        &.wheel-icon {
          background: var(--dragon-raised);
        }
        &.image-icon {
          background: var(--dragon-raised);
        }
      }
      .shortcut-title {
        font-size: 29rpx;
        font-weight: 600;
      }
      .shortcut-description {
        margin-top: 10rpx;
        color: var(--dragon-muted);
        font-size: 23rpx;
      }
      .shortcut-link {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 28rpx;
        color: var(--dragon-muted);
        font-size: 22rpx;
      }
    }
  }

  .menu-card {
    padding: 0 28rpx;
    border-radius: 24rpx;
    background: var(--dragon-surface);

    .menu-item {
      display: flex;
      align-items: center;
      min-height: 108rpx;

      &:not(:first-child) {
        border-top: 2rpx solid var(--dragon-border);
      }
      .menu-icon {
        display: flex;
        align-items: center;
        margin-right: 20rpx;
      }
      .menu-title {
        flex: 1;
        font-size: 27rpx;
      }
      .menu-note {
        margin-right: 12rpx;
        color: var(--dragon-muted);
        font-size: 22rpx;
      }
    }
  }

  .theme-settings {
    padding: 0 0 24rpx;

    .theme-label {
      display: block;
      margin-bottom: 14rpx;
      color: var(--dragon-muted);
      font-size: 23rpx;
    }

    .theme-options {
      display: flex;
      gap: 12rpx;

      .theme-option {
        flex: 1;
        margin: 0;
        border-radius: 14rpx;
        background: var(--dragon-raised);
        color: var(--dragon-text);
        font-size: 26rpx;

        &::after {
          border: none;
        }

        &.selected {
          background: var(--dragon-primary);
          color: #fff;
        }
      }
    }
  }

  .page-footer {
    display: flex;
    align-items: center;
    flex-direction: column;
    padding-top: 44rpx;
    color: var(--dragon-muted);

    .footer-name {
      font-size: 25rpx;
      font-weight: 600;
      letter-spacing: 2rpx;
    }
    .footer-description {
      margin-top: 10rpx;
      font-size: 21rpx;
    }
  }
}
</style>
