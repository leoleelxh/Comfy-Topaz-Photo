# Changelog

## [1.0.0] - 2025-04-19

### Added
- 全新的智能图像格式处理系统，支持多种 PyTorch 张量格式
- 新增 `find_output_file` 辅助函数，能智能查找 Topaz 处理后的输出文件
- 新增 `output_prefix` 可选参数，允许用户自定义输出文件名前缀
- 更全面的日志系统，提供详细的处理信息和错误诊断

### Fixed
- 修复了处理 PyTorch 张量时的格式兼容问题，现可正确处理 [B, H, W, C]、[C, H, W] 等多种格式
- 修复了输出文件检测逻辑，能够找到 Topaz 使用不同命名规则的输出文件
- 修复了临时文件清理机制中的异常处理问题
- 改进了图像加载过程，添加了 EXIF 方向处理和图像模式转换

### Changed
- 重构了 `process_topaz_image` 函数，添加了多重检测方法和重试机制
- 改进了 `save_images` 函数，现在能处理更多图像格式和异常情况
- 优化了输出图像的后处理逻辑，与 ComfyUI 更好地兼容
- 更新了错误处理机制，确保即使在处理失败时也能返回原始图像

### Improved
- 大幅提高了与 Topaz Photo AI 的通信可靠性
- 优化了图像处理流程，提供更详细的调试信息
- 增强了错误恢复能力，添加了自动重试机制
- 更清晰的日志输出，方便用户排查问题

## [Unreleased] - 2025-04-12

### Fixed
- Resolved compatibility issues with newer versions of Topaz Photo AI CLI (`tpai.exe`).
  - Addressed `UnicodeDecodeError` by explicitly using UTF-8 encoding when reading `tpai.exe` output.
  - Handled `AttributeError: 'NoneType' object has no attribute 'find'` by adding checks for empty `stdout` before parsing.
  - Investigated and worked around internal `tpai.exe` error `[json.exception.type_error.302] type must be number, but is string` by adjusting parameter formatting and ultimately only passing the `model` parameter alongside `--override`.
  - Addressed internal `tpai.exe` error `Could not load model` which occurred when only `--override` and `--upscale`/`--sharpen` were passed without any sub-parameters. The fix involves passing the required `model` parameter.
  - Added `--override` flag when manual settings (upscale or sharpen) are enabled to prevent issues with merging settings with Autopilot.
- Improved robustness of `__init__.py` when copying JavaScript files.

### Changed
- Renamed Python classes and ComfyUI node identifiers to `ComfyTopazPhoto` prefix for consistency.
  - `TopazPhotoAI` -> `ComfyTopazPhoto`
  - `TopazUpscaleSettings` -> `ComfyTopazPhotoUpscaleSettings`
  - `TopazSharpenSettings` -> `ComfyTopazPhotoSharpenSettings`
  - Updated `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`.
  - Updated JavaScript extension directory name in `__init__.py`.
- Updated logging prefixes to `ComfyTopazPhoto:`.

### Deprecated
- Passing detailed sub-parameters (like `scale`, `denoise`, `compression`, etc.) via the command line is temporarily disabled due to incompatibilities with the current `tpai.exe` version. The node will now use Topaz Photo AI's default values for these parameters when upscale/sharpen is enabled via the settings nodes, only overriding the `model`. 