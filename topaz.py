import os
import sys
import platform
import subprocess
import time
import tempfile
import uuid
import shutil
import glob
from PIL import Image, ImageOps
import numpy as np
import torch  # 添加导入 torch 模块

# 日志前缀
log_prefix = "[ComfyTopazPhoto]"

# 通过以下更新解决了关键问题:
# 1. 改进的图像格式处理，支持各种 PyTorch 张量格式
# 2. 更健壮的文件查找算法，确保能找到 Topaz 处理后的图片
# 3. 更好的错误处理和日志记录
# 4. 清理临时文件的安全机制
# 5. 与 ComfyUI 更好的兼容性

# Topaz Photo AI 异常类
class TopazError(Exception):
    """Topaz Photo AI 相关错误的异常类"""
    pass

def init_topaz(custom_path=None):
    """
    初始化 Topaz Photo AI，查找可执行文件
    参数:
        custom_path (str, optional): 用户指定的 tpai.exe 路径
    返回: 
        (executable_path, version_string)
    """
    # 如果提供了自定义路径，先检查它
    if custom_path and os.path.isfile(custom_path):
        try:
            result = subprocess.run(f'"{custom_path}" --version', shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            version = result.stdout.strip() if result.returncode == 0 else "未知版本"
            print(f"{log_prefix} 使用自定义路径 Topaz Photo AI: {custom_path} (版本: {version})")
            return (custom_path, version)
        except Exception as e:
            print(f"{log_prefix} 警告: 找到 Topaz Photo AI 但无法获取版本: {custom_path}, 错误: {str(e)}")
            return (custom_path, "未知版本")
    
    # 如果未提供自定义路径或自定义路径无效，尝试标准路径
    executable_paths = []
    
    # Windows 路径
    if platform.system() == "Windows":
        # Topaz Photo AI 安装路径
        paths = [
            os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Topaz Labs LLC', 'Topaz Photo AI', 'tpai.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Topaz Labs LLC', 'Topaz Photo AI', 'tpai.exe'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Topaz Labs LLC', 'Topaz Photo AI', 'tpai.exe'),
        ]
        executable_paths.extend(paths)
    
    # macOS 路径
    elif platform.system() == "Darwin":
        paths = [
            '/Applications/Topaz Photo AI.app/Contents/MacOS/tpai',
            os.path.expanduser('~/Applications/Topaz Photo AI.app/Contents/MacOS/tpai')
        ]
        executable_paths.extend(paths)
    
    # Linux 路径 (如果支持)
    elif platform.system() == "Linux":
        paths = [
            '/opt/topaz-photo-ai/tpai',
            os.path.expanduser('~/.local/share/Topaz Labs LLC/Topaz Photo AI/tpai')
        ]
        executable_paths.extend(paths)
    
    # 检查路径是否存在
    for path in executable_paths:
        if os.path.isfile(path):
            # 尝试获取版本
            try:
                result = subprocess.run(f'"{path}" --version', shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                version = result.stdout.strip() if result.returncode == 0 else "未知版本"
                print(f"{log_prefix} 找到 Topaz Photo AI: {path} (版本: {version})")
                return (path, version)
            except Exception as e:
                print(f"{log_prefix} 警告: 找到 Topaz Photo AI 但无法获取版本: {path}, 错误: {str(e)}")
                return (path, "未知版本")
    
    # 没有找到可执行文件
    if custom_path:
        raise TopazError(f"无法使用自定义路径: {custom_path}。文件不存在或无法访问。")
    else:
        raise TopazError(f"未找到 Topaz Photo AI 可执行文件。请提供正确的 tpai.exe 路径或确保已正确安装 Topaz Photo AI。")

def process_topaz_image(tpai_exe, input_images, output_folder, output_format="jpg", quality=95, overwrite=False):
    """
    使用 Topaz Photo AI 处理图像
    
    参数:
        tpai_exe (str): Topaz Photo AI 可执行文件路径
        input_images (list): 输入图像路径列表
        output_folder (str): 输出文件夹
        output_format (str): 输出格式 (jpg, png, tif, etc.)
        quality (int): JPEG 质量 (0-100)
        overwrite (bool): 是否覆盖现有文件
        
    返回:
        list: 处理后的图像路径列表
    """
    # 验证输入
    if not tpai_exe or not os.path.exists(tpai_exe):
        raise TopazError(f"Topaz Photo AI 可执行文件未找到: {tpai_exe}")
    
    if not input_images:
        raise TopazError("没有输入图像")
    
    # 确保输出文件夹存在
    try:
        os.makedirs(output_folder, exist_ok=True)
        print(f"{log_prefix} 输出文件夹: {output_folder}")
    except Exception as e:
        raise TopazError(f"无法创建输出文件夹: {output_folder}, 错误: {str(e)}")
    
    output_images = []
    max_retries = 2  # 最大重试次数
    
    # 处理每个输入图像
    for input_path in input_images:
        if not os.path.exists(input_path):
            print(f"{log_prefix} 警告: 输入图像不存在: {input_path}")
            continue
        
        print(f"{log_prefix} 处理图像: {input_path}")
        
        # 检查是否已经有处理过的文件
        existing_file = find_output_file(input_path, output_folder, output_format)
        if existing_file and not overwrite:
            print(f"{log_prefix} 输出文件已存在且不覆盖: {existing_file}")
            output_images.append(existing_file)
            continue
        
        # 记录处理前的文件列表
        before_files = set(os.listdir(output_folder)) if os.path.exists(output_folder) else set()
        
        # 构建命令
        cmd = [
            f'"{tpai_exe}"',
            f'"{input_path}"',
            f'--output "{output_folder}"',
            f'--format {output_format}',
            f'--quality {quality}',
            f'--showSettings' # 显示处理设置
        ]
        
        if overwrite:
            cmd.append('--overwrite')
        
        # 执行命令
        command = " ".join(cmd)
        print(f"{log_prefix} 执行命令: {command}")
        
        for retry in range(max_retries + 1):
            try:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    encoding='utf-8', 
                    errors='ignore',
                    timeout=300  # 设置超时时间为5分钟
                )
                
                # 输出详细日志用于调试
                print(f"{log_prefix} 命令返回码: {result.returncode}")
                print(f"{log_prefix} 命令标准输出: {result.stdout[:500]}...")  # 只显示前500个字符
                if result.stderr:
                    print(f"{log_prefix} 命令错误输出: {result.stderr}")
                
                # 检查是否成功
                if result.returncode == 0:
                    # 尝试查找输出文件
                    output_file = find_output_file(input_path, output_folder, output_format)
                    if output_file:
                        print(f"{log_prefix} 成功处理图像: {input_path} -> {output_file}")
                        output_images.append(output_file)
                        break  # 成功处理，退出重试循环
                    else:
                        # 查找处理后的新文件
                        after_files = set(os.listdir(output_folder))
                        new_files = after_files - before_files
                        
                        # 按文件创建时间排序，获取最新的文件
                        if new_files:
                            new_file_paths = [os.path.join(output_folder, f) for f in new_files]
                            # 按修改时间排序
                            new_file_paths.sort(key=os.path.getmtime, reverse=True)
                            output_path = new_file_paths[0]
                            print(f"{log_prefix} 成功处理图像(通过新文件检测): {input_path} -> {output_path}")
                            output_images.append(output_path)
                            break
                        else:
                            error_msg = f"Topaz Photo AI 可能处理成功但未检测到输出文件"
                            if retry < max_retries:
                                print(f"{log_prefix} {error_msg}，第 {retry+1} 次重试...")
                                time.sleep(2)  # 等待2秒后重试
                            else:
                                print(f"{log_prefix} {error_msg}，已达最大重试次数。")
                                raise TopazError(error_msg)
                else:
                    error_msg = f"处理图像失败: {result.stderr if result.stderr else '未知错误'}"
                    if retry < max_retries:
                        print(f"{log_prefix} {error_msg}，第 {retry+1} 次重试...")
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        print(f"{log_prefix} 错误代码: {result.returncode}")
                        print(f"{log_prefix} 标准输出: {result.stdout}")
                        print(f"{log_prefix} 错误输出: {result.stderr}")
                        raise TopazError(error_msg)
            
            except subprocess.TimeoutExpired:
                error_msg = f"处理图像超时: {input_path}"
                if retry < max_retries:
                    print(f"{log_prefix} {error_msg}，第 {retry+1} 次重试...")
                    time.sleep(2)  # 等待2秒后重试
                else:
                    print(f"{log_prefix} {error_msg}，已达最大重试次数。")
                    raise TopazError(error_msg)
            
            except Exception as e:
                error_msg = f"执行异常: {str(e)}"
                if retry < max_retries:
                    print(f"{log_prefix} {error_msg}，第 {retry+1} 次重试...")
                    time.sleep(2)  # 等待2秒后重试
                else:
                    print(f"{log_prefix} {error_msg}，已达最大重试次数。")
                    raise TopazError(f"Topaz Photo AI 执行异常: {str(e)}")
    
    if not output_images:
        print(f"{log_prefix} 警告: 没有处理任何图像")
    else:
        print(f"{log_prefix} 成功处理 {len(output_images)} 个图像")
    
    return output_images

def save_images(images, file_prefix="temp_", file_suffix=".png"):
    """
    保存图像到临时文件
    
    参数:
        images (list): PyTorch张量、PIL图像或numpy数组列表
        file_prefix (str): 文件名前缀
        file_suffix (str): 文件后缀
        
    返回:
        list: 保存的文件路径列表
    """
    saved_paths = []
    
    # 确保是列表
    if not isinstance(images, list):
        images = [images]
    
    for img in images:
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(
            prefix=file_prefix, 
            suffix=file_suffix,
            delete=False
        )
        temp_file.close()
        
        try:
            # 转换为PIL图像并保存
            if isinstance(img, torch.Tensor):
                # 从PyTorch张量转换为PIL图像
                image_np = img.cpu().numpy()
                
                # 打印调试信息
                print(f"{log_prefix} 张量形状: {image_np.shape}, 类型: {image_np.dtype}, 值范围: {image_np.min()} - {image_np.max()}")
                
                # 处理批次维度 (如果有)
                if len(image_np.shape) == 4:  # [B, H, W, C] 或 [B, C, H, W]
                    # 提取第一个批次
                    image_np = image_np[0]
                
                # 处理图像数据格式，确保是 [H, W, C]
                if len(image_np.shape) == 3:
                    if image_np.shape[0] == 3 or image_np.shape[0] == 4:  # [C, H, W] 格式
                        # 转换为 [H, W, C]
                        image_np = np.transpose(image_np, (1, 2, 0))
                
                # 确保值范围在 0-255
                if image_np.max() <= 1.0:
                    image_np = image_np * 255.0
                
                # 裁剪值到 0-255 并转换为 uint8
                image_np = np.clip(image_np, 0, 255).astype(np.uint8)
                
                # 根据通道数创建不同模式的图像
                if image_np.ndim == 3 and image_np.shape[2] == 3:
                    pil_img = Image.fromarray(image_np, 'RGB')
                elif image_np.ndim == 3 and image_np.shape[2] == 4:
                    pil_img = Image.fromarray(image_np, 'RGBA')
                elif image_np.ndim == 2 or (image_np.ndim == 3 and image_np.shape[2] == 1):
                    if image_np.ndim == 3:
                        image_np = image_np[:, :, 0]
                    pil_img = Image.fromarray(image_np, 'L')
                else:
                    # 尝试直接转换
                    pil_img = Image.fromarray(image_np)
                
                pil_img.save(temp_file.name)
                
            elif isinstance(img, np.ndarray):
                # 从numpy数组转换为PIL图像
                image_np = img.copy()
                
                # 打印调试信息
                print(f"{log_prefix} 数组形状: {image_np.shape}, 类型: {image_np.dtype}, 值范围: {image_np.min()} - {image_np.max()}")
                
                # 确保值范围在 0-255
                if image_np.max() <= 1.0:
                    image_np = image_np * 255.0
                
                # 裁剪值到 0-255 并转换为 uint8
                image_np = np.clip(image_np, 0, 255).astype(np.uint8)
                
                # 根据通道数创建不同模式的图像
                if image_np.ndim == 3 and image_np.shape[2] == 3:
                    pil_img = Image.fromarray(image_np, 'RGB')
                elif image_np.ndim == 3 and image_np.shape[2] == 4:
                    pil_img = Image.fromarray(image_np, 'RGBA')
                elif image_np.ndim == 2 or (image_np.ndim == 3 and image_np.shape[2] == 1):
                    if image_np.ndim == 3:
                        image_np = image_np[:, :, 0]
                    pil_img = Image.fromarray(image_np, 'L')
                else:
                    # 尝试直接转换
                    pil_img = Image.fromarray(image_np)
                
                pil_img.save(temp_file.name)
                
            elif isinstance(img, Image.Image):
                # 直接保存PIL图像
                img.save(temp_file.name)
            else:
                raise ValueError(f"不支持的图像类型: {type(img)}")
            
            saved_paths.append(temp_file.name)
            
        except Exception as e:
            print(f"{log_prefix} 保存图像时出错: {str(e)}")
            # 如果出错，删除临时文件
            if os.path.exists(temp_file.name):
                try:
                    os.remove(temp_file.name)
                except:
                    pass
            raise e
    
    return saved_paths

def load_images(file_paths):
    """
    加载图像文件为PIL图像
    
    参数:
        file_paths (list): 图像文件路径列表
        
    返回:
        list: PIL图像列表
    """
    images = []
    
    # 确保是列表
    if not isinstance(file_paths, list):
        file_paths = [file_paths]
    
    for path in file_paths:
        try:
            # 检查文件是否存在
            if not os.path.exists(path):
                print(f"{log_prefix} 警告: 图像文件不存在: {path}")
                continue
                
            print(f"{log_prefix} 正在加载图像: {path}")
            img = Image.open(path)
            
            # 尝试处理 EXIF 旋转
            try:
                img = ImageOps.exif_transpose(img)
            except Exception as exif_error:
                print(f"{log_prefix} 处理 EXIF 数据时出错 (非致命): {str(exif_error)}")
            
            # 确保图像为 RGB 模式
            if img.mode != "RGB":
                print(f"{log_prefix} 转换图像模式从 {img.mode} 到 RGB")
                img = img.convert("RGB")
                
            images.append(img)
            print(f"{log_prefix} 成功加载图像: {path}, 尺寸: {img.size}, 模式: {img.mode}")
            
        except Exception as e:
            print(f"{log_prefix} 加载图像失败: {path}, 错误: {str(e)}")
    
    if not images:
        print(f"{log_prefix} 警告: 未能加载任何图像")
    else:
        print(f"{log_prefix} 共加载了 {len(images)} 个图像")
        
    return images

def disable_topaz_image_cache():
    """禁用 Topaz Photo AI 的图像缓存"""
    # 这里简化实现
    print(f"{log_prefix} 尝试禁用 Topaz Photo AI 缓存")

def enable_topaz_image_cache():
    """启用 Topaz Photo AI 的图像缓存"""
    # 这里简化实现
    print(f"{log_prefix} 尝试启用 Topaz Photo AI 缓存")

def test_and_clean_topaz(tpai_exe, clean_cache=False, verbose=True):
    """
    测试 Topaz Photo AI 安装并清理缓存
    
    参数:
        tpai_exe (str): Topaz Photo AI 可执行文件路径
        clean_cache (bool): 是否清理缓存
        verbose (bool): 是否显示详细信息
        
    返回:
        dict: 测试结果
    """
    results = {
        "success": False,
        "error_message": "",
        "test_output": "",
        "cleaned_files": 0,
        "cache_size_before": 0,
        "cache_size_after": 0
    }
    
    # 检查 tpai_exe 路径是否有效
    if not os.path.exists(tpai_exe):
        results["error_message"] = f"Topaz Photo AI 可执行文件未找到: {tpai_exe}"
        if verbose:
            print(f"{log_prefix} {results['error_message']}")
        return results
    
    # 获取缓存目录路径
    cache_dir = ""
    if platform.system() == "Windows":
        cache_dir = os.path.expanduser("~/AppData/Local/Topaz Labs LLC/Topaz Photo AI/Cache")
    elif platform.system() == "Darwin":  # macOS
        cache_dir = os.path.expanduser("~/Library/Caches/Topaz Labs LLC/Topaz Photo AI")
    elif platform.system() == "Linux":
        cache_dir = os.path.expanduser("~/.cache/Topaz Labs LLC/Topaz Photo AI")
    
    # 检查缓存目录大小
    if clean_cache and os.path.exists(cache_dir):
        cache_size = sum(os.path.getsize(f) for f in glob.glob(os.path.join(cache_dir, '**/*'), recursive=True) if os.path.isfile(f))
        results["cache_size_before"] = cache_size
        if verbose:
            print(f"{log_prefix} 缓存目录: {cache_dir}")
            print(f"{log_prefix} 当前缓存大小: {cache_size/1024/1024:.2f} MB")
    
    # 1. 执行 Topaz Photo AI 测试命令
    try:
        if verbose:
            print(f"{log_prefix} 尝试执行测试命令: {tpai_exe} --test")
        
        # 执行测试命令
        result = subprocess.run(f'"{tpai_exe}" --test', 
                               shell=True, 
                               capture_output=True, 
                               text=True, 
                               encoding='utf-8', 
                               errors='ignore')
        
        results["test_output"] = result.stdout
        if result.stderr:
            results["test_output"] += f"\n错误输出:\n{result.stderr}"
            
        if verbose:
            print(f"{log_prefix} 测试命令返回码: {result.returncode}")
            print(f"{log_prefix} 测试命令输出: {result.stdout}")
            if result.stderr:
                print(f"{log_prefix} 测试命令错误: {result.stderr}")
        
        # 检查返回码
        if result.returncode == 0:
            results["success"] = True
            if verbose:
                print(f"{log_prefix} Topaz Photo AI 测试成功!")
        else:
            results["error_message"] = f"测试命令返回非零代码: {result.returncode}"
            if verbose:
                print(f"{log_prefix} {results['error_message']}")
    
    except Exception as e:
        results["error_message"] = f"执行测试命令时出错: {str(e)}"
        if verbose:
            print(f"{log_prefix} {results['error_message']}")
    
    # 2. 如果请求清理缓存
    if clean_cache and os.path.exists(cache_dir):
        try:
            if verbose:
                print(f"{log_prefix} 开始清理缓存目录: {cache_dir}")
            
            # 获取要删除的文件列表
            files_to_delete = []
            for file_pattern in ["*.tmp", "*.cache", "temp_*", "*.log"]:
                files_to_delete.extend(glob.glob(os.path.join(cache_dir, file_pattern)))
                files_to_delete.extend(glob.glob(os.path.join(cache_dir, "**", file_pattern), recursive=True))
            
            # 删除文件
            cleaned_count = 0
            for file_path in files_to_delete:
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        cleaned_count += 1
                        if verbose and cleaned_count % 10 == 0:  # 每清理10个文件记录一次
                            print(f"{log_prefix} 已清理 {cleaned_count} 个缓存文件...")
                except Exception as e:
                    if verbose:
                        print(f"{log_prefix} 无法删除文件 {file_path}: {str(e)}")
            
            results["cleaned_files"] = cleaned_count
            
            # 计算清理后的缓存大小
            if os.path.exists(cache_dir):
                cache_size_after = sum(os.path.getsize(f) for f in glob.glob(os.path.join(cache_dir, '**/*'), recursive=True) if os.path.isfile(f))
                results["cache_size_after"] = cache_size_after
                
                if verbose:
                    print(f"{log_prefix} 清理完成! 删除了 {cleaned_count} 个文件")
                    print(f"{log_prefix} 清理前缓存大小: {results['cache_size_before']/1024/1024:.2f} MB")
                    print(f"{log_prefix} 清理后缓存大小: {cache_size_after/1024/1024:.2f} MB")
                    print(f"{log_prefix} 节省空间: {(results['cache_size_before'] - cache_size_after)/1024/1024:.2f} MB")
        
        except Exception as e:
            if verbose:
                print(f"{log_prefix} 清理缓存时出错: {str(e)}")
    
    return results

def find_output_file(input_path, output_folder, output_format):
    """
    查找 Topaz 处理后的输出文件。
    Topaz 可能使用不同的命名规则，所以我们需要尝试多种方式。
    
    参数:
        input_path (str): 原始输入文件路径
        output_folder (str): 输出文件夹
        output_format (str): 输出文件格式
        
    返回:
        str: 找到的输出文件路径，如果未找到则返回 None
    """
    # 方法1：使用相同的文件名（不含扩展名）
    base_name = os.path.basename(input_path)
    name_without_ext = os.path.splitext(base_name)[0]
    
    # 尝试找到确切匹配的文件
    exact_match = os.path.join(output_folder, f"{name_without_ext}.{output_format}")
    if os.path.exists(exact_match):
        return exact_match
    
    # 方法2：使用相同文件名的任何可能变体
    possible_matches = glob.glob(os.path.join(output_folder, f"{name_without_ext}*.{output_format}"))
    if possible_matches:
        # 按修改时间排序，返回最新的
        possible_matches.sort(key=os.path.getmtime, reverse=True)
        return possible_matches[0]
    
    # 方法3：返回最新创建的任何输出格式文件
    all_files = []
    for ext in ["jpg", "jpeg", "png", "tif", "tiff"]:
        all_files.extend(glob.glob(os.path.join(output_folder, f"*.{ext}")))
    
    if all_files:
        # 按修改时间排序，返回最新的
        all_files.sort(key=os.path.getmtime, reverse=True)
        return all_files[0]
    
    # 方法4：捕获任何文件
    all_files = glob.glob(os.path.join(output_folder, "*"))
    if all_files:
        # 按修改时间排序，返回最新的
        all_files.sort(key=os.path.getmtime, reverse=True)
        return all_files[0]
    
    # 找不到任何文件
    return None

# 简化的 ComfyTopazPhoto 类
class ComfyTopazPhoto:
    def __init__(self):
        # 不再自动查找可执行文件，而是在 process_images 方法中使用用户提供的路径
        self.tpai_version = "未知版本"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "tpai_exe": ("STRING", {"default": "C:\\Program Files\\Topaz Labs LLC\\Topaz Photo AI\\tpai.exe"}),
                "output_format": (["jpg", "png", "tif", "tiff", "preserve"], {"default": "jpg"}),
                "quality": ("INT", {"default": 95, "min": 0, "max": 100, "step": 1}),
                "overwrite": (["True", "False"], {"default": "False"}),
            },
            "optional": {
                "output_prefix": ("STRING", {"default": "topaz_", "multiline": False}),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process_images"
    CATEGORY = "ComfyTopazPhoto"
    
    def process_images(self, images, tpai_exe, output_format="jpg", quality=95, overwrite="False", output_prefix="topaz_"):
        """处理图像"""
        # 将字符串转换为布尔值
        overwrite = (overwrite == "True")
        
        # 验证 tpai_exe 路径
        try:
            self.tpai_exe, self.tpai_version = init_topaz(tpai_exe)
            print(f"{log_prefix} 使用 Topaz Photo AI: {self.tpai_exe} (版本: {self.tpai_version})")
        except TopazError as e:
            raise e
        
        # 创建临时输出文件夹
        output_folder = tempfile.mkdtemp(prefix="topaz_output_")
        input_paths = []  # 初始化为空列表
        
        try:
            # 打印输入图像信息用于调试
            print(f"{log_prefix} 输入图像形状: {images.shape}")
            
            # 保存输入图像到临时文件
            timestamp = int(time.time())
            file_prefix = f"{output_prefix}{timestamp}_"
            input_paths = save_images(images, file_prefix=file_prefix)
            print(f"{log_prefix} 已保存输入图像到: {input_paths}")
            
            # 调用 Topaz Photo AI 处理图像
            output_paths = process_topaz_image(
                self.tpai_exe, 
                input_paths, 
                output_folder, 
                output_format, 
                quality, 
                overwrite
            )
            
            print(f"{log_prefix} 处理后图像路径: {output_paths}")
            
            # 如果没有处理任何图像，返回原图
            if not output_paths:
                print(f"{log_prefix} 警告: 没有成功处理任何图像，返回原图")
                return (images,)
            
            # 直接使用参考代码中的图像加载方法
            upscaled_images = []
            for upscaled_path in output_paths:
                try:
                    # 打开图像，应用EXIF方向
                    img = Image.open(upscaled_path)
                    img = ImageOps.exif_transpose(img)
                    img = img.convert('RGB')  # 确保是RGB模式
                    
                    # 转换为numpy数组，再转为PyTorch格式
                    img_np = np.array(img).astype(np.float32) / 255.0
                    # 添加批次维度 [H, W, C] -> [1, H, W, C]
                    img_tensor = torch.from_numpy(img_np)[None,]  
                    
                    upscaled_images.append(img_tensor)
                    print(f"{log_prefix} 成功加载处理后图像: {upscaled_path}, 形状: {img_tensor.shape}")
                except Exception as e:
                    print(f"{log_prefix} 加载图像失败: {upscaled_path}, 错误: {str(e)}")
            
            # 如果没有成功加载任何图像，返回原图
            if not upscaled_images:
                print(f"{log_prefix} 警告: 没有成功加载任何处理后的图像，返回原图")
                return (images,)
            
            # 如果有多个图像，合并为一个批次
            if len(upscaled_images) > 1:
                # 合并所有张量为一个批次
                result = torch.cat(upscaled_images, dim=0)
            else:
                # 只有一个图像，直接返回
                result = upscaled_images[0]
                
            print(f"{log_prefix} 最终输出图像形状: {result.shape}")
            return (result,)
        
        except Exception as e:
            print(f"{log_prefix} 处理图像时出错: {str(e)}")
            # 如果出错，返回原图
            return (images,)
            
        finally:
            # 清理临时文件
            try:
                # 清理输入临时文件
                for path in input_paths:
                    if os.path.exists(path):
                        try:
                            os.remove(path)
                            print(f"{log_prefix} 已删除临时输入文件: {path}")
                        except Exception as e:
                            print(f"{log_prefix} 清理临时输入文件失败: {path}, 错误: {str(e)}")
                
                # 清理临时输出文件夹
                if os.path.exists(output_folder):
                    try:
                        shutil.rmtree(output_folder)
                        print(f"{log_prefix} 已删除临时输出文件夹: {output_folder}")
                    except Exception as e:
                        print(f"{log_prefix} 清理临时输出文件夹失败: {output_folder}, 错误: {str(e)}")
            except Exception as e:
                print(f"{log_prefix} 清理临时文件失败: {str(e)}")

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "ComfyTopazPhoto": ComfyTopazPhoto,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyTopazPhoto": "Topaz Photo AI",
}

# 初始化和测试函数 - 现在作为一个可调用的函数而不是自动执行
def init_and_test_topaz(custom_path=None):
    """初始化并测试 Topaz Photo AI"""
    try:
        tpai_exe, version = init_topaz(custom_path)
        print(f"{log_prefix} 找到 Topaz Photo AI: {tpai_exe} (版本: {version})")
        
        # 测试 Topaz Photo AI
        test_results = test_and_clean_topaz(tpai_exe, False, True)
        if test_results["success"]:
            print(f"{log_prefix} Topaz Photo AI 测试成功!")
        else:
            print(f"{log_prefix} Topaz Photo AI 测试失败: {test_results['error_message']}")
        
        return True
    except Exception as e:
        print(f"{log_prefix} 初始化 Topaz Photo AI 失败: {str(e)}")
        return False

# 不再自动初始化测试，避免启动时错误
# init_and_test_topaz()
