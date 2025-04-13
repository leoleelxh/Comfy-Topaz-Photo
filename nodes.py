import os
import sys
import folder_paths
import comfy.model_management as model_management

from .topaz import (
    init_topaz,
    test_and_clean_topaz,
    ComfyTopazPhoto,
    NODE_CLASS_MAPPINGS as TOPAZ_NODE_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as TOPAZ_NODE_DISPLAY_NAME_MAPPINGS
)

# 添加测试和清理节点
class ComfyTopazPhotoTestAndClean:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tpai_exe": ("STRING", {"default": "C:\\Program Files\\Topaz Labs LLC\\Topaz Photo AI\\tpai.exe"}),
                "clean_cache": (["True", "False"], {"default": "False"}),
                "verbose": (["True", "False"], {"default": "True"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "FLOAT", "FLOAT",)
    RETURN_NAMES = ("status", "message", "cleaned_files", "cache_before_MB", "cache_after_MB",)
    FUNCTION = "test_and_clean"
    CATEGORY = "ComfyTopazPhoto"

    def test_and_clean(self, tpai_exe, clean_cache, verbose):
        # 将字符串转换为布尔值
        clean_cache = (clean_cache == "True")
        verbose = (verbose == "True")
        
        # 验证 tpai_exe 路径是否存在
        if not os.path.exists(tpai_exe):
            return ("ERROR", f"Topaz Photo AI 可执行文件未找到: {tpai_exe}", 0, 0.0, 0.0)
        
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

# 合并节点映射
NODE_CLASS_MAPPINGS = {
    **TOPAZ_NODE_CLASS_MAPPINGS,
    "ComfyTopazPhotoTestAndClean": ComfyTopazPhotoTestAndClean,
}

# 合并显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    **TOPAZ_NODE_DISPLAY_NAME_MAPPINGS,
    "ComfyTopazPhotoTestAndClean": "Test & Clean Topaz",
} 