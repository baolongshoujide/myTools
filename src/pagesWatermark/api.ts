import type { WatermarkHealth, WatermarkJob, WatermarkSubmitOptions } from '@/types/watermark'

// Local development only. Remote uniCloud integration will replace this transport.
export const serviceUrl = (
  import.meta.env.VITE_WATERMARK_API_URL || 'http://127.0.0.1:8765'
).replace(/\/$/, '')

const localServiceUnavailableMessage = '连接不到本机图片处理服务。请在项目根目录运行 pnpm fwq，并保持窗口开启。'

const checkManualSupport = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: serviceUrl + '/health',
      timeout: 10000,
      success: (response) => {
        const data = response.data as WatermarkHealth
        if (response.statusCode !== 200 || !data?.manualSelection) {
          reject(new Error('请先重启电脑端图片处理服务，再使用手动圈选'))
          return
        }
        resolve()
      },
      fail: () => reject(new Error(localServiceUnavailableMessage)),
    })
  })
}

export const submitImage = async (filePath: string, options: WatermarkSubmitOptions = { mode: 'auto' }): Promise<WatermarkJob> => {
  if (options.mode === 'manual') await checkManualSupport()
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: serviceUrl + '/jobs',
      filePath,
      name: 'file',
      formData: {
        mode: options.mode,
        regions: JSON.stringify(options.regions || []),
      },
      timeout: 60000,
      success: (response) => {
        try {
          const data = JSON.parse(response.data)
          if (response.statusCode !== 202) {
            reject(new Error(data.detail || '上传失败，请稍后重试'))
            return
          }
          resolve(data)
        } catch {
          reject(new Error('服务返回异常，请稍后重试'))
        }
      },
      fail: () => reject(new Error(localServiceUnavailableMessage)),
    })
  })
}

export const getJob = (id: string): Promise<WatermarkJob> => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: serviceUrl + '/jobs/' + encodeURIComponent(id),
      timeout: 15000,
      success: (response) => {
        if (response.statusCode !== 200) {
          reject(new Error('无法获取处理进度，请稍后重试'))
          return
        }
        resolve(response.data as WatermarkJob)
      },
      fail: () => reject(new Error('图片处理服务连接中断。请确认 pnpm fwq 对应的终端仍在运行。')),
    })
  })
}

export const imageUrl = (id: string, filename: string) => {
  return serviceUrl + '/jobs/' + encodeURIComponent(id) + '/' + filename
}
