直接回答

以下是关于通过命令行接口（CLI）调用 Topaz Photo AI（tpai.exe）的官方指定参数和开发文档的简要说明，以及如何在 ComfyUI 中进行集成的指导。由于 CLI 功能的复杂性和官方文档的局限性，我会尽量提供清晰的建议，但请注意，某些功能可能需要额外的配置或未来更新。

*   官方参数和文档：Topaz Photo AI 的 CLI 使用 Autopilot 设置（需在 GUI 中配置），支持基本的输出选项如格式、质量等，但目前无法直接通过 CLI 传递特定增强设置（如锐化、降噪）。
    
*   ComfyUI 集成：需要创建自定义节点，通过 Python 调用 tpai.exe，处理图像并返回结果，但需先在 GUI 中设置 Autopilot。
    

官方 CLI 参数

Topaz Photo AI 的 CLI 位于 C:\\Program Files\\Topaz Labs LLC\\Topaz Photo AI\\tpai.exe，基本用法为：

*   运行命令：.\\tpai.exe "path/to/image/or/folder"。
    
*   关键选项包括：
    
    *   \--output, -o <folder>：指定输出文件夹。
        
    *   \--format, -f <format>：设置输出格式（如 jpg、png）。
        
    *   \--quality, -q <0-100>：设置 JPEG 质量，默认 95。
        

详细参数见下表：

| 

选项



 | 

描述



 | 

值/备注



 |
| --- | --- | --- |
| 

\--output, -o <folder>



 | 

指定输出文件夹



 | 

如果文件夹不存在，将自动创建



 |
| 

\--overwrite



 | 

允许覆盖现有文件，注意此操作具有破坏性



 | 

\-



 |
| 

\--recursive, -r



 | 

如果提供文件夹路径，递归处理子目录中的所有图像



 | 

\-



 |
| 

\--format, -f <format>



 | 

设置输出格式



 | 

jpg

,

jpeg

,

png

,

tif

,

tiff

,

dng

,

preserve

（默认：

preserve

）



 |
| 

\--quality, -q <0-100>



 | 

设置 JPEG 质量



 | 

默认：95



 |
| 

\--compression, -c <0-10>



 | 

设置 PNG 压缩级别



 | 

默认：2



 |
| 

\`--bit-depth, -d <8



 | 

16>\`



 | 

设置 TIFF 位深度



 |
| 

\`--tiff-compression, -tc <none



 | 

lzw



 | 

zip>\`



 |

*   注意：增强设置（如锐化、降噪）依赖于 GUI 中的 Autopilot 配置，无法通过 CLI 直接控制。
    

在 ComfyUI 中的集成

ComfyUI 是一个基于节点的 Stable Diffusion 接口，您需要创建自定义节点来调用 tpai.exe：

*   步骤：
    
    1.  在 ComfyUI/custom\_nodes 下创建新目录（如 TopazPhotoAI）。
        
    2.  编写 Python 脚本，接受图像输入，保存为临时文件，调用 CLI 处理后加载结果。
        
    3.  示例代码见下文，需确保 Autopilot 设置已配置。
        
*   限制：由于 CLI 依赖 GUI 设置，灵活性有限，建议关注 Topaz Labs 的未来更新。
    

* * *

详细报告

以下是关于 Topaz Photo AI CLI 调用和 ComfyUI 集成的详细分析，基于官方文档和相关资源，旨在为开发提供全面指导。当前时间为 2025 年 4 月 13 日星期日 15:53 HKT，所有信息均基于此时间点可用的资料。

背景与概述

Topaz Photo AI 是一款由 Topaz Labs 开发的照片增强软件，适用于锐化、降噪和上采样等任务。它提供了一个命令行接口（CLI），通过 tpai.exe 允许用户在脚本或自动化流程中调用功能。官方文档位于 [Topaz Photo AI CLI 官方文档](https://docs.topazlabs.com/photo-ai/command-line-interface)，提供了 CLI 的基本用法和参数。

用户希望了解 CLI 的指定参数和开发文档，并特别关注如何在 ComfyUI 中调用。ComfyUI 是一个基于节点的 Stable Diffusion 接口，广泛用于 AI 图像生成，允许通过自定义节点扩展功能。

官方 CLI 文档分析

根据官方文档，tpai.exe 位于 C:\\Program Files\\Topaz Labs LLC\\Topaz Photo AI，基本用法如下：

*   打开命令提示符或终端，导航至安装目录：
    
    ```bash
    cd "C:\Program Files\Topaz Labs LLC\Topaz Photo AI"
    ```
    
*   查看帮助信息：
    
*   处理图像或文件夹：
    
    ```bash
    .\tpai.exe "path/to/image/or/folder"
    ```
    

处理机制

CLI 的图像处理依赖于 Autopilot 设置，这些设置需在 Topaz Photo AI 的 GUI 中配置，具体路径为 Preferences > Autopilot。相关配置指南见 [Autopilot 配置](https://docs.topazlabs.com/photo-ai/enhancements/autopilot-and-configuration)。这意味着，CLI 无法直接通过命令传递特定的增强参数（如锐化强度、降噪级别），而是使用 GUI 中预设的设置。

可用 CLI 选项

以下是官方文档中列出的 CLI 选项，整理为表格形式：

| 

选项



 | 

描述



 | 

值/备注



 |
| --- | --- | --- |
| 

\--output, -o <folder>



 | 

指定输出文件夹



 | 

如果文件夹不存在，将自动创建



 |
| 

\--overwrite



 | 

允许覆盖现有文件，注意此操作具有破坏性



 | 

\-



 |
| 

\--recursive, -r



 | 

如果提供文件夹路径，递归处理子目录中的所有图像



 | 

\-



 |
| 

\--format, -f <format>



 | 

设置输出格式



 | 

jpg

,

jpeg

,

png

,

tif

,

tiff

,

dng

,

preserve

（默认：

preserve

）

注意：RAW 文件即使选择

preserve

也会转换为 DNG



 |
| 

\--quality, -q <0-100>



 | 

设置 JPEG 质量



 | 

默认：95



 |
| 

\--compression, -c <0-10>



 | 

设置 PNG 压缩级别



 | 

默认：2



 |
| 

\`--bit-depth, -d <8



 | 

16>\`



 | 

设置 TIFF 位深度



 |
| 

\`--tiff-compression, -tc <none



 | 

lzw



 | 

zip>\`



 |

调试选项

*   \--showSettings：显示处理前的 Autopilot 设置。
    
*   \--skipProcessing：跳过实际处理，仅用于检查设置。
    
*   \--verbose, -v：增加控制台输出详细程度。
    

返回值

CLI 的返回代码如下：

*   0：成功
    
*   1：部分成功（部分文件处理失败）
    
*   \-1 (255)：未传递有效文件
    
*   \-2 (254)：无效日志令牌（可能需要通过 GUI 登录）
    
*   \-3 (253)：无效参数
    

局限性

从官方文档来看，CLI 当前不支持直接传递特定增强设置（如上采样比例、锐化强度），这可能限制其在自动化场景中的灵活性。社区论坛（如 [Topaz Community](https://community.topazlabs.com/t/cli-improvement-allow-input-arguments-for-enhancement-adjustments/43464)）中，用户已提出相关功能请求，但截至 2025 年 4 月 13 日，官方文档未反映此类更新。

ComfyUI 集成指南

ComfyUI 是一个基于节点的 Stable Diffusion 接口，允许用户通过自定义节点扩展功能。集成 Topaz Photo AI CLI 需要创建一个自定义节点，通过 Python 调用 tpai.exe，处理图像并返回结果。

创建自定义节点

1.  目录结构：
    
    *   在 ComfyUI/custom\_nodes 下创建新目录，例如 TopazPhotoAI。
        
    *   在该目录下创建 Python 文件，例如 topaz\_photo\_ai.py。
        
2.  节点实现：
    
    *   节点需继承 ComfyUI 的节点基类，定义输入输出和处理逻辑。
        
    *   示例代码如下，示意如何调用 CLI：
        
        ```python
        import os
        import subprocess
        from comfy.sd import SDNode
        
        class TopazPhotoAINode(SDNode):
            def __init__(self):
                super().__init__()
                self.input_image = None
                self.output_folder = None
                self.format = "preserve"
                self.quality = 95
        
            @classmethod
            def INPUT_TYPES(s):
                return {
                    "required": {
                        "image": ("IMAGE",),
                        "output_folder": ("STRING", {"default": "output"}),
                        "format": (["jpg", "jpeg", "png", "tif", "tiff", "dng", "preserve"],),
                        "quality": ("INT", {"default": 95, "min": 0, "max": 100}),
                    }
                }
        
            RETURN_TYPES = ("IMAGE",)
            RETURN_NAMES = ("processed_image",)
        
            def process(self, image, output_folder, format, quality):
                # 保存输入图像到临时文件
                temp_input_path = os.path.join(output_folder, "input.jpg")
                image.save(temp_input_path)
        
                # 构造 CLI 命令
                tpai_path = r"C:\Program Files\Topaz Labs LLC\Topaz Photo AI\tpai.exe"
                cmd = [
                    tpai_path,
                    temp_input_path,
                    "--output", output_folder,
                    "--format", format,
                    "--quality", str(quality),
                ]
        
                # 执行 CLI 命令
                subprocess.run(cmd, check=True)
        
                # 加载处理后的图像
                processed_image_path = os.path.join(output_folder, "output.jpg")  # 根据实际输出调整
                processed_image = Image.open(processed_image_path)
        
                return (processed_image,)
        NODE_CLASS_MAPPINGS = {
            "TopazPhotoAI": TopazPhotoAINode,
        }
        NODE_DISPLAY_NAME_MAPPINGS = {
            "TopazPhotoAI": "Topaz Photo AI",
        }
        ```
        
    *   说明：
        
        *   节点接受图像、输出文件夹、格式和质量作为输入。
            
        *   保存输入图像到临时文件，调用 tpai.exe，加载处理后的图像并返回。
            
        *   需确保输出文件夹存在或动态创建。
            
3.  安装与使用：
    
    *   将 topaz\_photo\_ai.py 放入 custom\_nodes/TopazPhotoAI 目录。
        
    *   重启 ComfyUI，节点“Topaz Photo AI”将出现在节点列表中。
        
    *   连接图像输入，配置输出文件夹、格式和质量，运行工作流处理图像。
        

集成限制

由于 CLI 依赖 Autopilot 设置，用户需在 Topaz Photo AI GUI 中预先配置这些设置，这可能限制灵活性。例如，无法通过节点动态调整锐化或降噪强度。社区讨论（如 [Topaz Community](https://community.topazlabs.com/t/ptai-cli-photo-ai-cli-allow-arguments-to-influence-settings/43464)）中，用户已表达希望 CLI 支持更多参数的愿望，但截至目前，官方文档未支持。

额外考虑

在开发过程中，注意以下几点：

*   文件路径管理：确保处理临时文件和输出文件时，路径正确且无权限问题。
    
*   性能优化：批量处理可能需要递归选项（\--recursive, -r），但需测试性能。
    
*   未来更新：如果 Topaz Labs 未来更新 CLI，支持更多参数（如增强设置），可相应调整节点逻辑。
    

相关资源与社区反馈

通过搜索发现，社区中存在一些 Python 脚本示例（如 [Topaz Photo AI CLI 示例](https://gist.github.com/mq1n/c46c0ae4de2fb72897ba13fa22826ab0)），但需注意，这些脚本可能涉及 Gigapixel AI 而非 Photo AI，需验证适用性。此外，Topaz Community 论坛（如 [CLI 改进建议](https://community.topazlabs.com/t/cli-improvement-allow-input-arguments-for-enhancement-adjustments/43464)）提供了用户需求反馈，可作为未来发展的参考。

结论

Topaz Photo AI 的 CLI 提供基本的图像处理功能，但增强设置依赖 GUI 配置，限制了自动化灵活性。在 ComfyUI 中集成需创建自定义节点，通过 Python 调用 CLI 处理图像，但需预先配置 Autopilot 设置。建议关注官方更新，获取更多 CLI 参数支持。

* * *

关键引用