from .topaz import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
import os
import shutil
import __main__

WEB_DIRECTORY = "./web"
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

# 确保 ComfyUI web 扩展目录存在
# 使用新的插件名称 "ComfyTopazPhoto" 作为子目录名
extensions_dir_name = "ComfyTopazPhoto"
comfy_dir = os.path.dirname(os.path.realpath(__main__.__file__))
extensions_path = os.path.join(comfy_dir, "web", "extensions", extensions_dir_name)

if not os.path.exists(extensions_path):
    os.makedirs(extensions_path)

# 将 web/js 目录下的所有 JS 文件复制到 ComfyUI 的 web/extensions/ComfyTopazPhoto 目录下
js_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "web", "js")
if os.path.isdir(js_path):
    for file in os.listdir(js_path):
        if file.endswith(".js"):
            src_file = os.path.join(js_path, file)
            dst_file = os.path.join(extensions_path, file)
            # 复制前先删除旧文件，确保更新
            if os.path.exists(dst_file):
                try:
                    os.remove(dst_file)
                except OSError as e:
                    print(f"Error removing existing JS file {dst_file}: {e}")
            try:
                shutil.copy(src_file, dst_file)
                print(f'ComfyTopazPhoto: Copied {file} to {extensions_path}')
            except shutil.Error as e:
                 print(f"Error copying JS file {src_file} to {dst_file}: {e}")
else:
    print(f"ComfyTopazPhoto: Warning - JS source directory not found: {js_path}")