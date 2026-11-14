# 开源来源

识别与修复功能复用 D-Ogi/WatermarkRemover-AI：
https://github.com/D-Ogi/WatermarkRemover-AI

固定版本：`127108a5bff1b880ad34ba26ac8b60710b69bb3b`。
`vendor/watermark_remover` 为该版本的图片处理相关源码子集，未改写上游文件。
保留其 MIT LICENSE、THIRD_PARTY_NOTICES.md 及 IOPaint Apache-2.0 许可证。
未复制桌面 GUI、视频界面和字体资源。

检测模型使用 Florence community 转换的 Florence-2-base（模型卡 MIT）：
https://huggingface.co/florence-community/Florence-2-base
固定版本：`00921df66db728a9ceb750f5eca43e5c203a2051`。
替代上游默认的大模型，以适应本项目电脑的 6GB 显存。

修复模型沿用上游的 big-lama.pt，由上游模块核对 SHA-256 和文件大小后加载。
模型权重及第三方依赖仍适用各自的授权条款，不因本项目代码开源而改变。
