# Changelog

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