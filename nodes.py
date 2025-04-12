import os
import sys
import folder_paths
import comfy.model_management as model_management

from .topaz import (
    init_topaz,
    process_topaz_image,
    disable_topaz_image_cache,
    enable_topaz_image_cache,
    test_and_clean_topaz
)

# ... existing code ...

class ComfyTopazPhotoModelLoader:
    # ... existing code ...

class ComfyTopazPhotoImageProcessor:
    # ... existing code ...

class ComfyTopazPhotoDisableCache:
    # ... existing code ...

class ComfyTopazPhotoEnableCache:
    # ... existing code ...    

# 添加新的节点，用于测试和清理 Topaz Photo AI
class ComfyTopazPhotoTestAndClean:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clean_cache": (["True", "False"], {"default": "False"}),
                "verbose": (["True", "False"], {"default": "True"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "FLOAT", "FLOAT",)
    RETURN_NAMES = ("status", "message", "cleaned_files", "cache_before_MB", "cache_after_MB",)
    FUNCTION = "test_and_clean"
    CATEGORY = "ComfyTopazPhoto"

    def test_and_clean(self, clean_cache, verbose):
        # 将字符串转换为布尔值
        clean_cache = (clean_cache == "True")
        verbose = (verbose == "True")
        
        # 获取 Topaz Photo AI 可执行文件路径
        try:
            tpai_exe = init_topaz()[0]
        except Exception as e:
            return ("ERROR", f"无法初始化 Topaz Photo AI: {str(e)}", 0, 0.0, 0.0)
        
        # 调用测试和清理函数
        results = test_and_clean_topaz(tpai_exe, clean_cache, verbose)
        
        # 构建状态和消息
        status = "SUCCESS" if results["success"] else "ERROR"
        
        message = ""
        if results["success"]:
            message = "Topaz Photo AI 测试成功!"
            if clean_cache:
                message += f" 已清理 {results['cleaned_files']} 个缓存文件。"
        else:
            message = f"测试失败: {results['error_message']}"
        
        # 计算缓存大小（MB）
        cache_before_MB = results["cache_size_before"] / 1024 / 1024
        cache_after_MB = results["cache_size_after"] / 1024 / 1024
        
        return (status, message, results["cleaned_files"], cache_before_MB, cache_after_MB)

# 节点列表
NODE_CLASS_MAPPINGS = {
    "ComfyTopazPhotoModelLoader": ComfyTopazPhotoModelLoader,
    "ComfyTopazPhotoImageProcessor": ComfyTopazPhotoImageProcessor,
    "ComfyTopazPhotoDisableCache": ComfyTopazPhotoDisableCache,
    "ComfyTopazPhotoEnableCache": ComfyTopazPhotoEnableCache,
    "ComfyTopazPhotoTestAndClean": ComfyTopazPhotoTestAndClean,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyTopazPhotoModelLoader": "Topaz Photo AI",
    "ComfyTopazPhotoImageProcessor": "Topaz Photo AI Processor",
    "ComfyTopazPhotoDisableCache": "Disable Topaz Cache",
    "ComfyTopazPhotoEnableCache": "Enable Topaz Cache",
    "ComfyTopazPhotoTestAndClean": "Test & Clean Topaz",
} 