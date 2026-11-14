# 本地验证记录

日期：2026-11-14。机器：i7-13620H、16GB RAM；当前安装的是 CPU 版 PyTorch。
RTX 4050 加速路径尚未验证，`setup.ps1 -UseCuda` 为可选安装路径。

## 已完成

- 安装独立 Python 3.12、CPU PyTorch 2.9.1、Transformers 4.57.6 等依赖；依赖兼容检查通过。
- Florence-2-base 固定版本文件通过 Git blob / SHA-256 校验；LaMA通过固定SHA-256校验。
- 小程序原生页面脚本、模板、样式编译通过；独立 TypeScript 检查通过。
- 完整微信小程序构建通过，输出到 `.runtime/mp-weixin-check`，包含 pagesWatermark 分包和首页入口。
- 实际HTTP接口验证：健康检查200、无效图片400、不存在任务404、繁忙时429。
- `validate_local.py` 经真实模型完成上传、识别、二次内容判断、修复、下载结果的端到端验证。

## 样图结果

使用验证程序自行生成的960×640山景插画，并在湖面叠加半透明英文文字水印。

- 带水印图：识别并修复1处，CPU约8.08秒。与已知干净背景相比，全图平均绝对像素误差从
  1.365降至0.063（0～255颜色范围），用于检查这张测试图片的修复效果。
- 无水印图：检测器最初将山景误识别为候选区域，二次描述检查拒绝修复；输出像素与输入一致，
  CPU约4.81秒。
- 第一轮没有二次判断时存在误删背景的问题；最终版本增加了候选区域描述检查，并重新通过上述测试。

这些结果不能推导为任意照片都能成功去水印。尚未验证批量真实照片、满屏重复水印、
人物细节遮挡、手机真机操作、相册权限交互、Android APK和HR外网访问。

本次结果保留在本机的 `.runtime/validation/check-report.json` 和 `outputs` 中。
本机已生成的对比图：`outputs/e360a3527a494081a35334da8e90aef7/comparison.png`（左原图、右结果）。

## 复测

先运行 `start-local.ps1`，另开终端执行：

```powershell
.\features\watermark\.venv\Scripts\python.exe .\features\watermark\validate_local.py
```

项目原有的全量 `pnpm type-check` 仍报 TS6504（CustomTabBar.vue.js 被作为JS根文件处理）。
本次对新分包单独运行类型检查通过，未改动项目原有类型检查配置。

## 未完成

uniCloud 服务空间尚未创建，因此未部署任务中转，也未做小程序正式联网域名和移动网络联调。
当前版本是可运行的本地开发版本，不应描述为已完成HR外网体验版。
