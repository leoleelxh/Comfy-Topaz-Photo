# ComfyUI Node for Topaz Photo AI (`ComfyTopazPhoto`)

![]sample.jpg

Integrate Topaz Photo AI's powerful image enhancement capabilities directly into your ComfyUI workflows.

This node allows you to call the `tpai.exe` command-line interface from within ComfyUI to apply enhancements offered by Topaz Photo AI through its Autopilot settings.

## 重要更新: v1.0.0 版本发布

我们很高兴地宣布 ComfyTopazPhoto 节点 v1.0.0 版本正式发布！此版本解决了多个关键问题并大幅提升了稳定性：

- **全新图像格式处理系统**：现在支持多种 PyTorch 张量格式，能够正确处理 ComfyUI 中的各种图像格式
- **智能输出文件检测**：新增 `find_output_file` 功能，能够在 Topaz 使用不同命名规则时仍能找到输出文件
- **出错后自动恢复**：添加了重试机制和更好的异常处理，确保在遇到问题时能继续工作
- **更详细的日志输出**：便于排查问题和了解处理过程

该扩展现已完全简化，专注于通过 Topaz Photo AI CLI 使用 Autopilot 设置进行基本图像处理。所有增强参数现在应该通过 Topaz Photo AI GUI 中的 Autopilot 设置进行配置。

## Requirements

*   **Licensed installation of Topaz Photo AI:** This node requires a working installation of Topaz Photo AI, specifically the `tpai.exe` executable.
*   **Topaz Photo AI Models:** Ensure that Topaz Photo AI has successfully downloaded the necessary AI models. You can usually verify this by running the main Topaz Photo AI application.

## Installation

1.  Clone this repository into your `ComfyUI/custom_nodes/` directory:
    ```bash
    git clone <your-repo-url> ComfyUI/custom_nodes/ComfyTopazPhoto
    ```
    (Replace `<your-repo-url>` with the actual URL of this repository)
2.  Alternatively, download the repository contents as a ZIP file and extract it into `ComfyUI/custom_nodes/ComfyTopazPhoto`.
3.  **Restart ComfyUI.**

## 使用流程详解

### 完整工作流程

使用 ComfyTopazPhoto 的完整流程包括以下几个步骤：

1. **安装前准备**
   - 确保 Topaz Photo AI 正确安装并激活
   - 确认 AI 模型已正确下载（可以通过打开 Topaz Photo AI 并处理一张测试图像来验证）
   - 确认 `tpai.exe` 的正确路径（通常在 `C:\Program Files\Topaz Labs LLC\Topaz Photo AI\tpai.exe`）

2. **配置 Autopilot 设置**
   - 打开 Topaz Photo AI 应用程序
   - 进入 **Preferences -> Autopilot**
   - 根据需要配置增强参数：
     * **Upscale & Resize**: 选择放大比例（2x、4x等）
     * **Face Recovery**: 调整面部恢复强度
     * **Sharpen**: 调整锐化程度
     * **Denoise**: 设置降噪级别
     * **文字恢复**: 如需要，启用文字恢复功能
   - 保存设置（这些设置将在 CLI 调用中使用）

3. **ComfyUI 工作流设置**
   - 在 ComfyUI 中，添加以下节点：
     * 图像源节点（例如 Load Image、VAE Decode 等）
     * **Topaz Photo AI** 节点：主处理节点
   - 连接图像源到 Topaz Photo AI 节点的 `images` 输入
   - 配置 Topaz Photo AI 节点参数：
     * `tpai_exe`: 设置 Topaz Photo AI 的可执行文件路径（例如 `C:\Program Files\Topaz Labs LLC\Topaz Photo AI\tpai.exe`）
     * `output_format`: 选择输出格式（jpg、png、tif等）
     * `quality`: 设置 JPEG 质量（对于jpg格式）
     * `overwrite`: 是否覆盖已存在的文件
     * `output_prefix`: (可选) 自定义输出文件前缀

4. **运行处理**
   - 运行工作流
   - ComfyUI 会自动调用 Topaz Photo AI 对图像进行处理
   - 处理完成后，增强后的图像将在 ComfyUI 中显示

5. **故障排除（如需）**
   - 如果遇到问题，可以在 ComfyUI 中添加 **Test & Clean Topaz** 节点
   - 设置 `tpai_exe` 为 Topaz Photo AI 的可执行文件路径
   - 设置 `clean_cache` 为 True 清理缓存
   - 设置 `verbose` 为 True 获取详细日志
   - 运行此节点测试 Topaz Photo AI 安装情况并清理缓存

### 实际使用案例

#### 基本图像增强工作流

```
[Load Image] --> [Topaz Photo AI] --> [Preview Image]
```

在这个简单工作流中：
1. 加载图像
2. 通过 Topaz Photo AI 节点处理（使用 Autopilot 预设的增强参数）
3. 预览结果

#### 与其他 ComfyUI 节点结合使用

```
[Load Image] --> [其他处理节点] --> [Topaz Photo AI] --> [后续处理节点] --> [Preview Image]
```

例如，你可以：
1. 使用 ComfyUI 的 SD 生成图像
2. 应用其他效果
3. 使用 Topaz Photo AI 进行最终的增强处理
4. 应用后期处理效果
5. 保存或预览结果

### 视觉流程示例

下面是一个简单的 ComfyUI 工作流程图示例：

```
+------------------+
| Load Image       |
+--------+---------+
         |
         v
+--------+---------+     +------------------+
| Topaz Photo AI   |     | Test & Clean     |
| tpai_exe: C:\... |     | tpai_exe: C:\... |
| output_format:jpg|     | clean_cache: True|
| quality: 95      |     +------------------+
+--------+---------+
         |
         v
+--------+---------+
| Preview Image    |
+------------------+
```

## 关键使用说明

- **必须正确设置 tpai_exe 路径**：这是 Topaz Photo AI 可执行文件的完整路径，例如 `C:\Program Files\Topaz Labs LLC\Topaz Photo AI\tpai.exe`
- **所有增强参数都通过 Topaz Photo AI 的 Autopilot 设置控制**，而不是通过 ComfyUI 节点参数
- Topaz Photo AI 应用程序和 ComfyUI 可以同时运行，但不要在 ComfyUI 处理图像时修改 Autopilot 设置
- 处理大图像可能需要较长时间，请耐心等待
- 所有临时文件会自动清理

## 节点详情

### Topaz Photo AI 节点

**输入:**
* `images`: 要处理的输入图像
* `tpai_exe`: Topaz Photo AI 可执行文件路径 (tpai.exe)
* `output_format`: 输出图像格式（jpg、png、tif、tiff、preserve）
* `quality`: JPEG 质量 (0-100, 默认: 95)
* `overwrite`: 是否覆盖现有文件
* `output_prefix`: (可选) 自定义输出文件前缀，默认为 "topaz_"

**输出:**
* `IMAGE`: 处理后的图像

### Test & Clean Topaz 节点

**输入:**
* `tpai_exe`: Topaz Photo AI 可执行文件路径 (tpai.exe)
* `clean_cache`: 是否清理 Topaz Photo AI 缓存
* `verbose`: 是否显示详细日志信息

**输出:**
* `status`: 测试状态（SUCCESS 或 ERROR）
* `message`: 测试结果消息
* `cleaned_files`: 已清理的缓存文件数量
* `cache_before_MB`: 清理前的缓存大小（MB）
* `cache_after_MB`: 清理后的缓存大小（MB）

## 查找 tpai.exe 路径

Topaz Photo AI 可执行文件 (tpai.exe) 通常位于以下位置：

* Windows: 
  * `C:\Program Files\Topaz Labs LLC\Topaz Photo AI\tpai.exe`
  * `C:\Program Files (x86)\Topaz Labs LLC\Topaz Photo AI\tpai.exe`
  * `%LOCALAPPDATA%\Topaz Labs LLC\Topaz Photo AI\tpai.exe`

* macOS:
  * `/Applications/Topaz Photo AI.app/Contents/MacOS/tpai`
  * `~/Applications/Topaz Photo AI.app/Contents/MacOS/tpai`

如果 Topaz Photo AI 安装在非标准位置，您需要手动找到并提供正确的路径。

## 高级使用技巧

### 批量处理
1. 使用 ComfyUI 的批处理功能加载多张图像
2. 连接到 Topaz Photo AI 节点
3. 所有图像将按顺序处理

### 不同增强设置切换
如果需要使用不同的增强设置处理不同批次的图像：
1. 处理第一批图像
2. 暂停 ComfyUI 工作流
3. 打开 Topaz Photo AI 修改 Autopilot 设置
4. 恢复 ComfyUI 工作流处理下一批图像

## 故障排除

### 常见问题

* **tpai.exe 路径错误**：确保提供正确的 Topaz Photo AI 可执行文件路径。你可以在 Windows 中右键点击 tpai.exe 文件，选择"属性"，然后复制"位置"中的路径

* **请确保 Topaz Photo AI 安装正确**：验证可以在命令行中运行 `tpai.exe --test`

* **确保已设置 Autopilot 设置**：所有增强设置都通过 Topaz Photo AI 的 Autopilot 进行控制，不再通过节点参数传递

* **处理失败**：查看控制台输出，可能是命令行参数问题。可以尝试使用 `Test & Clean Topaz` 节点清理缓存

* **图像质量不满意**：调整 Topaz Photo AI 的 Autopilot 设置，而不是节点参数

* **执行时间过长**：大图像处理可能需要较长时间；你也可以尝试清理缓存提高性能

### 新版本特有问题解决

* **图像格式兼容性错误**：如果看到类似 `Cannot handle this data type` 的错误，说明图像格式无法被正确处理。新版本已支持多种格式，但如果仍有问题，可尝试使用 ComfyUI 的格式转换节点先将图像转换为标准 RGB 格式。

* **"未找到输出文件"错误**：新版本引入了智能文件查找功能，应能解决大多数文件路径问题。如果仍然报错，请检查以下几点：
  * Topaz Photo AI 是否有足够权限写入临时目录
  * 临时目录路径中是否含有非英文字符
  * 检查 Topaz 应用程序本身是否可以正常处理图像

* **处理超时**：如果处理大图像时超时，可以尝试：
  * 先将图像缩小后再处理
  * 增加节点的超时时间（在代码中可配置，默认为5分钟）
  * 确保计算机有足够的内存和 GPU 资源

* **临时文件未删除**：如果发现临时文件未被清理，可能是因为处理过程中发生了异常。新版本改进了临时文件清理机制，如果仍有问题，可手动删除临时目录中的文件。

## 为什么简化？

原因很简单：根据官方文档，Topaz Photo AI CLI 实际上依赖于 GUI 中的 Autopilot 设置，而无法通过命令行参数直接控制增强参数。我们的简化版本专注于使用基本的 CLI 参数（如输出格式和质量），并让 Autopilot 设置控制所有增强功能。

这种方法有几个优点：
1. 更直观的界面
2. 更少的混淆（不再有看起来可以控制但实际无效的参数）
3. 更清晰的期望（用户知道需要在 GUI 中配置什么）
4. 简化的工作流程，减少潜在错误

## 后续改进

* 如果 Topaz Labs 更新 CLI 以支持更多直接参数控制，我们将相应更新扩展
* 考虑添加更多选项，如批处理模式和其他 CLI 支持的参数
* 计划添加预设功能，让用户可以保存和快速切换不同的 Autopilot 配置

