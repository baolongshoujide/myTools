import type { WatermarkJob } from '@/types/watermark'

// Local development only. Remote uniCloud integration will replace this transport.
export const serviceUrl = (
  import.meta.env.VITE_WATERMARK_API_URL || 'http://127.0.0.1:8765'
).replace(/\/$/, '')

export const submitImage = (filePath: string): Promise<WatermarkJob> => {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: serviceUrl + '/jobs',
      filePath,
      name: 'file',
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
      fail: () => reject(new Error('暂时无法连接图片处理服务，请稍后再试')),
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
      fail: () => reject(new Error('网络连接中断，请重新尝试')),
    })
  })
}

export const imageUrl = (id: string, filename: string) => {
  return serviceUrl + '/jobs/' + encodeURIComponent(id) + '/' + filename
}
