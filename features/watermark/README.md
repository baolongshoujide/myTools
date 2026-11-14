# 图片去水印（独立功能目录）

本阶段实现本地识别、LaMA 修复、开发接口以及 uni-app 原生操作页。
这是实际模型处理，不使用付费图片接口，也不把未检测到水印的图片标为修复成功。
尚未部署 uniCloud 中转，因此本阶段不能让外网 HR 直接使用。

## 目录

- `pipeline.py`：自动识别、生成蒙版、修复并保存对比结果。
- `server.py`：本地开发接口，默认仅监听本机 `127.0.0.1:8765`。
- `vendor/watermark_remover`：固定版本的开源源码及许可证。
- `setup.ps1`：安装独立 Python、依赖、下载模型。
- `run.ps1`：弹出 Windows 选图窗口，处理后打开结果目录。
- `start-local.ps1`：启动供小程序开发者工具调用的接口。
- `.runtime`、`.venv`、`models`、`outputs`：本地运行数据，不提交 Git。
- `../../src/pagesWatermark`：独立小程序分包，不含内嵌网页。

## 首次安装

在项目根目录的 PowerShell 运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\features\watermark\setup.ps1
```

安装到本目录，不更改 uni-app 的 npm 依赖。首次需要下载较大的 PyTorch 与模型文件。
默认安装较小的 CPU 版。若需要启用 RTX 显卡加速，可执行同一脚本并加 `-UseCuda`，
这会下载约2.7GB的显卡版 PyTorch。识别模型约442MB，LaMA约196MB。
需要联网访问 GitHub、Hugging Face、PyPI 和 PyTorch 官方下载源。
安装遇到网络错误可重新运行；模型准备完成后，缓存可供离线处理。

## 先用电脑验证真实效果

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\features\watermark\run.ps1
```

也可以指定图片：

```powershell
.\features\watermark\.venv\Scripts\python.exe .\features\watermark\pipeline.py "D:\Pictures\sample.jpg"
```

结果在 `outputs` 下的独立任务文件夹中：

- `original.png`：实际送入处理的图片。
- `detection.png`：红框标出自动识别的区域。
- `mask.png`：实际修复的蒙版。
- `result.png`：修复结果；未检测到时保留原图并明确报告。
- `comparison.png`：左原图、右结果。
- `report.json`：检测数量、耗时、尺寸、设备与结果状态。

默认输入不超过20MB或2400万像素，处理最长边1600像素，以控制笔记本资源占用。
可用 `--max-edge 2048` 调整上限。会在报告及小程序里明确提示缩放。
检测不是任意水印必成功：重复满屏水印、复杂背景和误识别需实际样图评估。
检测后会对候选区域做二次内容检查，不能确认的区域保留原样；该检查也可能漏掉真实水印，
不能保证所有无水印图片都不被误改，因此仍需对比结果。
模型为预训练模型；没有针对你的图片重新训练。

## 微信开发者工具联调

1. 运行 `start-local.ps1`，保持窗口运行。
2. 正常运行项目的 `pnpm dev:mp-weixin`。
3. 在微信开发者工具中进入首页的「图片去水印」。
4. 本地开发时需允许开发请求访问本机 HTTP 接口；仅用于开发调试。
5. 选择图片、自动去水印、比较原图与结果、保存到相册。

`http://127.0.0.1:8765` 指开发电脑自己，不是手机上的电脑地址。
当前启动脚本只允许本机访问，因此此默认配置适用于同一电脑上的开发者工具。
不要把开发接口直接暴露到互联网。
真机/HR 外网使用将在 uniCloud 中转接好并配置合法域名后验证。
服务地址可通过 `VITE_WATERMARK_API_URL` 在开发构建前配置，不在产品页面要求用户填写地址。

接口：`GET /health`、`POST /jobs`（multipart 字段 `file`）、
`GET /jobs/{id}`、`GET /jobs/{id}/result.png`。
一次只处理一个任务，繁忙时返回429。重启后旧任务不再可查询。
文件会保留在本机 `outputs`，可在停止服务后手动删除；目前未实现自动删除本地结果。

## 接下来部署的部分

免费 uniCloud 空间创建成功后，再接入图片存储、任务中转、电脑领取任务、访问控制、
云端图片到期清理、额度限制，并通过手机移动网络测试后再发布体验版。
云端只传递任务和图片，模型仍运行在你的电脑；不需要HR提供IP或调整配置。

开源来源与许可证见 `THIRD_PARTY.md`。

已执行的测试及其范围见 `VALIDATION.md`。
