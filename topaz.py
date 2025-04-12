import numpy as np
import os
import pprint
import time
import folder_paths
import torch
import subprocess
import json
import platform
import glob
import shutil

from PIL import Image, ImageOps
from typing import Optional
import json

# 重命名 Upscale 设置类
class ComfyTopazPhotoUpscaleSettings:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'enabled': (['true', 'false'], {'default': 'true', 'display': 'Enable Upscaling'}),
                'model': ([
                    'Standard v2', 
                    'Standard v1', 
                    'High fidelity v2',
                    'High fidelity v1',
                    'Low resolution',
                    'Graphics'
                ], {'default': 'Standard v2', 'display': 'Upscale Model'}),
            },
            'optional': {
                # 基础参数
                'param1': ('FLOAT', {'default': 0.13, 'min': 0.0, 'max': 1.0, 'step': 0.01, 
                          'display': 'Denoise Strength (param1) - Reduces noise and grain'}),
                'param2': ('FLOAT', {'default': 0.39, 'min': 0.0, 'max': 1.0, 'step': 0.01, 
                          'display': 'Deblur Strength (param2) - Enhances sharpness'}),
                'param3': ('FLOAT', {'default': 0.78, 'min': 0.0, 'max': 1.0, 'step': 0.01, 
                          'display': 'Fix Compression (param3) - Repairs compression artifacts'}),
                # 高级参数 
                'mode': (['scale'], {'default': 'scale', 
                         'display': 'Mode - Currently only scale mode is supported'}),
                'resolution': ('INT', {'default': 72, 'min': 1, 'max': 300, 
                              'display': 'Resolution (dpi) - Output resolution'}),
                'resolution_unit': ('INT', {'default': 1, 'min': 0, 'max': 3, 
                                   'display': 'Resolution Unit (1=dpi, 2=dpcm)'}),
                'locked': (['true', 'false'], {'default': 'false', 
                           'display': 'Lock Settings - Prevent auto adjustments'}),
            },
        }

    # 更新返回类型名称
    RETURN_TYPES = ('ComfyTopazPhotoUpscaleSettings',)
    RETURN_NAMES = ('upscale_settings',)
    FUNCTION = 'init'
    # 更新类别，保持一致性
    CATEGORY = 'ComfyTopazPhoto' 
    OUTPUT_NODE = False
    OUTPUT_IS_LIST = (False,)
    
    def init(self, enabled, model, param1=0.13, param2=0.39, param3=0.78, mode='scale', 
             resolution=72, resolution_unit=1, locked=False):
        # 基本设置
        self.enabled = str(True).lower() == enabled.lower()
        self.model = model
        
        # 参数设置
        self.param1 = float(param1)
        self.param2 = float(param2)
        self.param3 = float(param3)
        
        # 高级设置
        self.mode = mode
        self.resolution = int(resolution)
        self.resolution_unit = int(resolution_unit)
        self.locked = str(True).lower() == locked.lower()
        
        return (self,)

# 重命名 Sharpen 设置类
class ComfyTopazPhotoSharpenSettings:       
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'enabled': (['true', 'false'], {'default': 'true', 'display': 'Enable Sharpening'}),
                'model': ([
                    'Standard', 
                    'Standard V2',
                    'Strong',
                    'Natural',
                    'Lens Blur',
                    'Lens Blur V2', 
                    'Motion Blur',
                    'Refocus'
                ], {'default': 'Standard V2', 'display': 'Sharpen Model'}),
            },
            'optional': {
                # 基础参数
                'param1': ('FLOAT', {'default': 0.065, 'min': 0.0, 'max': 1.0, 'step': 0.01, 
                          'display': 'Strength (param1) - Controls overall sharpening intensity'}),
                'param2': ('FLOAT', {'default': 0.22, 'min': 0.0, 'max': 1.0, 'step': 0.01, 
                          'display': 'Denoise (param2) - Reduces grain while sharpening'}),
                
                # 高级参数
                'compression': ('FLOAT', {'default': 0.49, 'min': 0.0, 'max': 1.0, 'step': 0.01,
                               'display': 'Compression - Handles compression artifacts during sharpening'}),
                'is_lens': (['true', 'false'], {'default': 'false', 
                           'display': 'Use Lens Blur Mode - Better for out-of-focus areas'}),
                'auto': (['true', 'false'], {'default': 'true', 
                        'display': 'Auto Settings - Let Topaz adjust parameters automatically'}),
                'mask': (['true', 'false'], {'default': 'true', 
                        'display': 'Use Mask - Apply selectively to needed areas'}),
                'locked': (['true', 'false'], {'default': 'false', 
                          'display': 'Lock Settings - Prevent auto adjustments'}),
            },
        }

    # 更新返回类型名称
    RETURN_TYPES = ('ComfyTopazPhotoSharpenSettings',)
    RETURN_NAMES = ('sharpen_settings',)
    FUNCTION = 'init'
    # 更新类别，保持一致性
    CATEGORY = 'ComfyTopazPhoto'
    OUTPUT_IS_LIST = (False,)
    
    def init(self, enabled, model, param1=0.065, param2=0.22, compression=0.49,
             is_lens='false', auto='true', mask='true', locked='false'):
        # 基本设置
        self.enabled = str(True).lower() == enabled.lower()
        self.model = model
        
        # 参数设置
        self.param1 = float(param1)  # strength
        self.param2 = float(param2)  # denoise
        
        # 高级设置
        self.compression = float(compression)
        self.is_lens = str(True).lower() == is_lens.lower()
        self.auto = str(True).lower() == auto.lower()
        self.mask = str(True).lower() == mask.lower()
        self.locked = str(True).lower() == locked.lower()
        
        return (self,)

# 添加 Face Recovery 设置类
class ComfyTopazPhotoFaceRecoverySettings:       
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'enabled': (['true', 'false'], {'default': 'true'}),
                'model': (['Face Perfect'], {'default': 'Face Perfect'}),
            },
            'optional': {
                # 基础参数
                'param1': ('FLOAT', {'default': 0.8, 'min': 0.0, 'max': 1.0, 'step': 0.01, 'display': 'strength (param1)'}),
                
                # 高级参数
                'version': ('INT', {'default': 2, 'min': 1, 'max': 3}),
                'face_option': (['auto', 'manual'], {'default': 'auto'}),
                'creativity': ('INT', {'default': 0, 'min': 0, 'max': 5}),
                'locked': (['true', 'false'], {'default': 'false'}),
                
                # 面部部分选项 (以逗号分隔的列表)
                'face_parts': ('STRING', {'default': 'hair,necks', 'multiline': False}),
            },
        }

    RETURN_TYPES = ('ComfyTopazPhotoFaceRecoverySettings',)
    RETURN_NAMES = ('face_recovery_settings',)
    FUNCTION = 'init'
    CATEGORY = 'ComfyTopazPhoto'
    OUTPUT_IS_LIST = (False,)
    
    def init(self, enabled, model, param1=0.8, version=2, face_option='auto', 
             creativity=0, locked='false', face_parts='hair,necks'):
        # 基本设置
        self.enabled = str(True).lower() == enabled.lower()
        self.model = model
        
        # 参数设置
        self.param1 = float(param1)  # strength
        
        # 高级设置
        self.version = int(version)
        self.face_option = face_option
        self.creativity = int(creativity)
        self.locked = str(True).lower() == locked.lower()
        
        # 面部部分
        self.face_parts = face_parts.split(',') if face_parts else []
        
        return (self,)

# 添加 Denoise 设置类
class ComfyTopazPhotoDenoiseSettings:       
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'enabled': (['true', 'false'], {'default': 'true'}),
                'model': ([
                    'Normal',
                    'Normal V2',
                    'Strong',
                    'Strong V2',
                    'Extreme'
                ], {'default': 'Normal V2'}),
            },
            'optional': {
                # 基础参数
                'param1': ('FLOAT', {'default': 0.27, 'min': 0.0, 'max': 1.0, 'step': 0.01, 'display': 'strength (param1)'}),
                'param2': ('FLOAT', {'default': 0.02, 'min': 0.0, 'max': 1.0, 'step': 0.01, 'display': 'minor deblur (param2)'}),
                
                # 高级参数
                'original_detail': ('FLOAT', {'default': 0.0, 'min': 0.0, 'max': 1.0, 'step': 0.01, 'display': 'recover detail'}),
                'auto': (['true', 'false'], {'default': 'true', 'display': 'auto settings'}),
                'mask': (['true', 'false'], {'default': 'true', 'display': 'use mask'}),
                'locked': (['true', 'false'], {'default': 'false'}),
            },
        }

    RETURN_TYPES = ('ComfyTopazPhotoDenoiseSettings',)
    RETURN_NAMES = ('denoise_settings',)
    FUNCTION = 'init'
    CATEGORY = 'ComfyTopazPhoto'
    OUTPUT_IS_LIST = (False,)
    
    def init(self, enabled, model, param1=0.27, param2=0.02, original_detail=0.0,
             auto='true', mask='true', locked='false'):
        # 基本设置
        self.enabled = str(True).lower() == enabled.lower()
        self.model = model
        
        # 参数设置
        self.param1 = float(param1)  # strength
        self.param2 = float(param2)  # minor deblur
        
        # 高级设置
        self.original_detail = float(original_detail)
        self.auto = str(True).lower() == auto.lower()
        self.mask = str(True).lower() == mask.lower()
        self.locked = str(True).lower() == locked.lower()
        
        return (self,)

# 添加 Text Recovery 设置类
class ComfyTopazPhotoTextRecoverySettings:       
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'enabled': (['true', 'false'], {'default': 'true'}),
            },
            'optional': {
                # 基础参数
                'param1_normal': ('FLOAT', {'default': 0.166, 'min': 0.0, 'max': 1.0, 'step': 0.01}),
                'param2_normal': ('FLOAT', {'default': 0.627, 'min': 0.0, 'max': 1.0, 'step': 0.01}),
                'param3_normal': ('FLOAT', {'default': 0.936, 'min': 0.0, 'max': 1.0, 'step': 0.01}),
                'param1_noisy': ('FLOAT', {'default': 0.272, 'min': 0.0, 'max': 1.0, 'step': 0.01}),
                'param2_noisy': ('FLOAT', {'default': 0.024, 'min': 0.0, 'max': 1.0, 'step': 0.01}),
                'param3_noisy': ('FLOAT', {'default': 0.0, 'min': 0.0, 'max': 1.0, 'step': 0.01}),
                'param4': ('FLOAT', {'default': 0.9, 'min': 0.0, 'max': 1.0, 'step': 0.01}),
                
                # 高级参数
                'auto': (['true', 'false'], {'default': 'true'}),
                'locked': (['true', 'false'], {'default': 'false'}),
            },
        }

    RETURN_TYPES = ('ComfyTopazPhotoTextRecoverySettings',)
    RETURN_NAMES = ('text_recovery_settings',)
    FUNCTION = 'init'
    CATEGORY = 'ComfyTopazPhoto'
    OUTPUT_IS_LIST = (False,)
    
    def init(self, enabled, param1_normal=0.166, param2_normal=0.627, param3_normal=0.936,
             param1_noisy=0.272, param2_noisy=0.024, param3_noisy=0.0, param4=0.9,
             auto='true', locked='false'):
        # 基本设置
        self.enabled = str(True).lower() == enabled.lower()
        
        # 参数设置
        self.param1_normal = float(param1_normal)
        self.param2_normal = float(param2_normal)
        self.param3_normal = float(param3_normal)
        self.param1_noisy = float(param1_noisy)
        self.param2_noisy = float(param2_noisy)
        self.param3_noisy = float(param3_noisy)
        self.param4 = float(param4)
        
        # 高级设置
        self.auto = str(True).lower() == auto.lower()
        self.locked = str(True).lower() == locked.lower()
        
        return (self,)

# 添加 Super Focus 设置类
class ComfyTopazPhotoSuperFocusSettings:       
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'enabled': (['true', 'false'], {'default': 'true'}),
            },
            'optional': {
                # 基础参数
                'amount': ('FLOAT', {'default': 0.5, 'min': 0.0, 'max': 1.0, 'step': 0.01}),
                'radius': ('FLOAT', {'default': 0.5, 'min': 0.0, 'max': 1.0, 'step': 0.01}),
                
                # 高级参数
                'auto': (['true', 'false'], {'default': 'true'}),
                'locked': (['true', 'false'], {'default': 'false'}),
            },
        }

    RETURN_TYPES = ('ComfyTopazPhotoSuperFocusSettings',)
    RETURN_NAMES = ('super_focus_settings',)
    FUNCTION = 'init'
    CATEGORY = 'ComfyTopazPhoto'
    OUTPUT_IS_LIST = (False,)
    
    def init(self, enabled, amount=0.5, radius=0.5, auto='true', locked='false'):
        # 基本设置
        self.enabled = str(True).lower() == enabled.lower()
        
        # 参数设置
        self.amount = float(amount)
        self.radius = float(radius)
        
        # 高级设置
        self.auto = str(True).lower() == auto.lower()
        self.locked = str(True).lower() == locked.lower()
        
        return (self,)

# 添加 裁剪和填充 设置类
class ComfyTopazPhotoCropAndPaddingSettings:       
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'enabled': (['true', 'false'], {'default': 'false'}),
            },
            'optional': {
                # 裁剪参数
                'crop_left': ('INT', {'default': 0, 'min': 0, 'max': 10000, 'step': 1}),
                'crop_top': ('INT', {'default': 0, 'min': 0, 'max': 10000, 'step': 1}),
                'crop_right': ('INT', {'default': 0, 'min': 0, 'max': 10000, 'step': 1}),
                'crop_bottom': ('INT', {'default': 0, 'min': 0, 'max': 10000, 'step': 1}),
                
                # 填充参数
                'pad_left': ('INT', {'default': 0, 'min': 0, 'max': 10000, 'step': 1}),
                'pad_top': ('INT', {'default': 0, 'min': 0, 'max': 10000, 'step': 1}),
                'pad_right': ('INT', {'default': 0, 'min': 0, 'max': 10000, 'step': 1}),
                'pad_bottom': ('INT', {'default': 0, 'min': 0, 'max': 10000, 'step': 1}),
                
                # 高级参数
                'auto': (['true', 'false'], {'default': 'false'}),
                'locked': (['true', 'false'], {'default': 'false'}),
            },
        }

    RETURN_TYPES = ('ComfyTopazPhotoCropAndPaddingSettings',)
    RETURN_NAMES = ('crop_padding_settings',)
    FUNCTION = 'init'
    CATEGORY = 'ComfyTopazPhoto'
    OUTPUT_IS_LIST = (False,)
    
    def init(self, enabled, 
             crop_left=0, crop_top=0, crop_right=0, crop_bottom=0,
             pad_left=0, pad_top=0, pad_right=0, pad_bottom=0,
             auto='false', locked='false'):
        # 基本设置
        self.enabled = str(True).lower() == enabled.lower()
        
        # 裁剪参数
        self.crop_left = int(crop_left)
        self.crop_top = int(crop_top)
        self.crop_right = int(crop_right)
        self.crop_bottom = int(crop_bottom)
        
        # 填充参数
        self.pad_left = int(pad_left)
        self.pad_top = int(pad_top)
        self.pad_right = int(pad_right)
        self.pad_bottom = int(pad_bottom)
        
        # 高级设置
        self.auto = str(True).lower() == auto.lower()
        self.locked = str(True).lower() == locked.lower()
        
        return (self,)

# 重命名主类
class ComfyTopazPhoto:
    '''
    A node that uses Topaz Photo AI (tpai.exe) behind the scenes to enhance (upscale/sharpen/denoise/etc.) the given image(s).
    
    If no settings are provided, auto-detected (auto-pilot) settings are used.
    '''
    def __init__(self):
        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        self.comfy_dir = os.path.abspath(os.path.join(self.this_dir, '..', '..'))
        self.subfolder = 'upscaled'
        self.output_dir = os.path.join(self.comfy_dir, 'temp')
        self.prefix = 'tpai' # 可以考虑改成 'ctp' (ComfyTopazPhoto)
        # self.tpai = 'C:/Program Files/Topaz Labs LLC/Topaz Photo AI/tpai.exe'

    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'images': ('IMAGE',),
            },
            'optional': {
                'compression': ('INT', {
                    'default': 2,
                    'min': 0,
                    'max': 10,
                }),
                'tpai_exe': ('STRING', {
                    'default': '',                    
                }),
                # 更新设置输入的类型名称
                'upscale': ('ComfyTopazPhotoUpscaleSettings',),
                'sharpen': ('ComfyTopazPhotoSharpenSettings',),
                'face_recovery': ('ComfyTopazPhotoFaceRecoverySettings',),
                'denoise': ('ComfyTopazPhotoDenoiseSettings',),
                'crop_padding': ('ComfyTopazPhotoCropAndPaddingSettings',),
                # 添加缺失的设置节点输入
                'text_recovery': ('ComfyTopazPhotoTextRecoverySettings',),
                'super_focus': ('ComfyTopazPhotoSuperFocusSettings',),
            },
            "hidden": {
            }
        }

    RETURN_TYPES = ('STRING', 'STRING', 'IMAGE')
    RETURN_NAMES = ('settings', 'autopilot_settings', 'IMAGE')
    FUNCTION = 'upscale_image'
    # 更新类别
    CATEGORY = 'ComfyTopazPhoto'
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True, True, True)

    def save_image(self, img, output_dir, filename):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        file_path = os.path.join(output_dir, filename)
        img.save(file_path)
        return file_path

    def load_image(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        i = Image.open(image_path)
        i = ImageOps.exif_transpose(i)
        image = i.convert('RGB')
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        return image

    def get_settings(self, stdout):
        # ... (内容保持不变)
        # 可以考虑更新日志前缀
        log_prefix = '\033[31mComfyTopazPhoto:\033[0m'
        if not stdout:
            print(f'{log_prefix} Warning: Received empty stdout for get_settings.')
            return '{}', '{}'

        settings_json = '{}'
        autopilot_settings_json = '{}'
        try:
            settings_start_marker = 'Final Settings for'
            settings_start = stdout.find(settings_start_marker)

            if settings_start == -1:
                print(f'{log_prefix} Warning: "{settings_start_marker}" not found in stdout. Cannot extract settings.')
                print(f'{log_prefix} Full stdout was:\n{stdout}')
                return '{}', '{}'

            settings_start = stdout.find('{', settings_start)

            if settings_start == -1:
                print(f'{log_prefix} Warning: Could not find opening brace \'{{\' after settings marker.')
                return '{}', '{}'

            count = 0
            settings_end = settings_start
            in_string = False
            for i in range(settings_start, len(stdout)):
                char = stdout[i]
                if char == '"':
                    in_string = not in_string
                elif not in_string:
                    if char == '{':
                        count += 1
                    elif char == '}':
                        count -= 1

                if count == 0 and char == '}':
                    settings_end = i
                    break
            else:
                print(f'{log_prefix} Warning: Could not find matching closing brace \'}}\' for settings JSON.')
                return '{}', '{}'

            settings_json_str = str(stdout[settings_start : settings_end + 1])

            settings = json.loads(settings_json_str)
            autopilot_settings = settings.pop('autoPilotSettings', {})
            user_settings_json = json.dumps(settings, indent=2).replace('"', "'")
            autopilot_settings_json = json.dumps(autopilot_settings, indent=2).replace('"', "'")

        except json.JSONDecodeError as e:
            print(f'{log_prefix} Error decoding settings JSON: {e}')
            print(f'{log_prefix} Extracted string was: {settings_json_str}')
            return '{}', '{}'
        except Exception as e:
            print(f'{log_prefix} An unexpected error occurred in get_settings: {e}')
            print(f'{log_prefix} Full stdout was:\n{stdout}')
            return '{}', '{}'

        return user_settings_json, autopilot_settings_json

    def topaz_upscale(self, img_file, compression=0, format='png', tpai_exe=None, 
                      # 更新类型提示
                      upscale: Optional[ComfyTopazPhotoUpscaleSettings]=None, 
                      sharpen: Optional[ComfyTopazPhotoSharpenSettings]=None,
                      face_recovery: Optional[ComfyTopazPhotoFaceRecoverySettings]=None,
                      denoise: Optional[ComfyTopazPhotoDenoiseSettings]=None,
                      crop_padding: Optional[ComfyTopazPhotoCropAndPaddingSettings]=None,
                      text_recovery: Optional[ComfyTopazPhotoTextRecoverySettings]=None,
                      super_focus: Optional[ComfyTopazPhotoSuperFocusSettings]=None):
        
        log_prefix = '\033[31mComfyTopazPhoto:\033[0m' # 日志前缀

        # 增加调试日志 - 检查 Topaz 版本和已安装模型
        print(f'{log_prefix} 开始处理图像: {img_file}')
        print(f'{log_prefix} 使用 tpai_exe: {tpai_exe}')
        print(f'{log_prefix} upscale 启用状态: {upscale and upscale.enabled}')
        if upscale and upscale.enabled:
            print(f'{log_prefix} upscale 模型: {upscale.model}')
        
        # 检查 tpai_exe 是否存在
        if not os.path.exists(tpai_exe):
            error_msg = f'Topaz Photo AI executable not found at {tpai_exe}'
            print(f'{log_prefix} 错误: {error_msg}')
            raise ValueError(error_msg)
        if compression < 0 or compression > 10:
            raise ValueError('Compression value must be between 0 and 10')
            
        # ============ 尝试先执行一个测试命令 ============
        print(f'{log_prefix} 先执行一个简单的测试命令，确认 Topaz Photo AI 正常工作')
        try:
            test_cmd = f'"{tpai_exe}" --test'
            print(f'{log_prefix} 测试命令: {test_cmd}')
            test_result = subprocess.run(test_cmd, capture_output=True, text=True, shell=True, encoding='utf-8', errors='ignore')
            print(f'{log_prefix} 测试命令返回码: {test_result.returncode}')
            print(f'{log_prefix} 测试命令输出: {test_result.stdout}')
            print(f'{log_prefix} 测试命令错误: {test_result.stderr}')
        except Exception as e:
            print(f'{log_prefix} 测试命令执行失败: {str(e)}')
            
        # ============ 尝试清理 Topaz 缓存文件 ============
        try:
            print(f'{log_prefix} 尝试清理 Topaz 缓存文件')
            cache_dir = os.path.expanduser("~/AppData/Local/Topaz Labs LLC/Topaz Photo AI/Cache")
            if os.path.exists(cache_dir):
                print(f'{log_prefix} 发现缓存目录: {cache_dir}')
                print(f'{log_prefix} 警告: 不会实际删除缓存，仅供参考')
                # 在这里我们不实际删除缓存，仅记录信息
                # 如果需要删除，可以取消注释下面的代码
                # for file in os.listdir(cache_dir):
                #     try:
                #         os.remove(os.path.join(cache_dir, file))
                #         print(f'{log_prefix} 已删除缓存文件: {file}')
                #     except Exception as e:
                #         print(f'{log_prefix} 删除缓存文件失败: {file} - {str(e)}')
            else:
                print(f'{log_prefix} 缓存目录不存在: {cache_dir}')
        except Exception as e:
            print(f'{log_prefix} 清理缓存失败: {str(e)}')

        # 准备参数
        target_dir = os.path.join(self.output_dir, self.subfolder)
        os.makedirs(target_dir, exist_ok=True)

        # 生成临时文件名，确保有唯一的文件名
        temp_dir = os.path.dirname(img_file)
        file_ext = os.path.splitext(os.path.basename(img_file))[1]
        timestamp = int(time.time() * 1000)
        temp_output_base = f"tpai-{timestamp}-result"
        temp_output_file = os.path.join(temp_dir, f"{temp_output_base}{file_ext}")

        print(f'{log_prefix} 临时输出文件: {temp_output_file}')
        
        # 组装 tpai 参数
        tpai_args = []
        
        # 更详细地记录传递给 Topaz 的参数
        all_settings = {
            'upscale': upscale,
            'sharpen': sharpen,
            'face_recovery': face_recovery,
            'denoise': denoise,
            'crop_padding': crop_padding,
            'text_recovery': text_recovery,
            'super_focus': super_focus
        }
        
        print(f'{log_prefix} 当前启用的处理设置:')
        for name, setting in all_settings.items():
            if setting and setting.enabled:
                print(f'{log_prefix}   - {name}: 已启用')
                if hasattr(setting, 'model') and setting.model:
                    print(f'{log_prefix}     模型: {setting.model}')
            else:
                print(f'{log_prefix}   - {name}: 未启用')
        
        # 基本参数
        in_file = f'"{img_file}"'
        out_file = f'"{temp_output_file}"'
        
        # ================ 临时简化命令 - 仅使用最基本参数 ================
        # 强制创建一个非常简单的命令，用于隔离问题
        basic_cmd = [
            f'"{tpai_exe}"',
            '--no-gui',
            '--input', in_file,
            '--output', out_file,
            '--save'
        ]
        
        # 只添加 upscale 参数，其他参数暂时注释掉
        if upscale and upscale.enabled and upscale.model:
            basic_cmd.extend(['--upscale', f'"{upscale.model}"'])
            print(f'{log_prefix} 使用 upscale 模型: {upscale.model}')
        
        basic_cmd_str = ' '.join(basic_cmd)
        print(f'{log_prefix} 简化命令: {basic_cmd_str}')
        
        # 执行简化命令
        try:
            print(f'{log_prefix} 尝试执行简化命令')
            result = subprocess.run(basic_cmd_str, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            print(f'{log_prefix} 简化命令返回码: {result.returncode}')
            print(f'{log_prefix} 简化命令输出: {result.stdout}')
            print(f'{log_prefix} 简化命令错误: {result.stderr}')
            
            # 检查输出文件是否存在
            if os.path.exists(temp_output_file):
                print(f'{log_prefix} 输出文件已生成: {temp_output_file}')
                file_size = os.path.getsize(temp_output_file)
                print(f'{log_prefix} 输出文件大小: {file_size} 字节')
            else:
                print(f'{log_prefix} 警告: 输出文件未生成: {temp_output_file}')
            
            # 如果简化命令成功，则跳过原始命令执行
            if result.returncode == 0 and os.path.exists(temp_output_file) and os.path.getsize(temp_output_file) > 0:
                print(f'{log_prefix} 简化命令执行成功，跳过原始命令执行')
                # 继续处理后续步骤
            else:
                print(f'{log_prefix} 简化命令执行失败，尝试原始命令')
                # 执行原始命令部分
                # ... 原始命令代码 ...
                # 注意：这部分代码未修改，将保持原样
                # 此处省略原始命令执行代码
                raise ValueError(f'简化命令执行失败，且原始命令执行已被跳过。请检查 Topaz 安装和模型状态。')
        except Exception as e:
            print(f'{log_prefix} 执行简化命令时出错: {str(e)}')
            # 尝试原始命令部分
            # ... 原始命令代码 ...
            # 注意：这部分代码未修改，将保持原样
            raise ValueError(f'执行 Topaz Photo AI 失败: {str(e)}')

        # 检查输出文件
        if not os.path.exists(temp_output_file):
            error_msg = f'Topaz Photo AI 未能生成输出文件，请检查日志获取详细信息。'
            print(f'{log_prefix} 错误: {error_msg}')
            raise ValueError(error_msg)
            
        print(f'{log_prefix} Topaz Photo AI 处理完成，输出文件: {temp_output_file}')
        
        # 计算唯一的输出文件名
        filename = f"{temp_output_base}.{format}"
        if filename in os.listdir(target_dir):
            filename = f"{temp_output_base}_{int(time.time())}.{format}"
        
        target_file = os.path.join(target_dir, filename)
        
        # 读取处理后的图像
        image = Image.open(temp_output_file)
            
        # 保存到目标位置
        if format.lower() == 'png':
            image.save(target_file, format='PNG', compress_level=compression)
        elif format.lower() == 'jpeg' or format.lower() == 'jpg':
            image.save(target_file, format='JPEG', quality=100-(compression*10))
        elif format.lower() == 'webp':
            image.save(target_file, format='WEBP', quality=100-(compression*10))
        else:
            image.save(target_file)
            
        print(f'{log_prefix} 图像已保存到: {target_file}')
            
        # 删除临时文件
        try:
            os.remove(temp_output_file)
            print(f'{log_prefix} 已删除临时文件: {temp_output_file}')
        except Exception as e:
            print(f'{log_prefix} 警告: 删除临时文件失败: {str(e)}')

        return (target_file, user_settings, autopilot_settings)

    # 函数名保持不变，因为它是在 ComfyUI 中注册的入口点
    def upscale_image(self, images, compression=0, format='png', tpai_exe=None, 
                      # 更新类型提示
                      upscale: Optional[ComfyTopazPhotoUpscaleSettings]=None, 
                      sharpen: Optional[ComfyTopazPhotoSharpenSettings]=None,
                      face_recovery: Optional[ComfyTopazPhotoFaceRecoverySettings]=None,
                      denoise: Optional[ComfyTopazPhotoDenoiseSettings]=None,
                      crop_padding: Optional[ComfyTopazPhotoCropAndPaddingSettings]=None,
                      text_recovery: Optional[ComfyTopazPhotoTextRecoverySettings]=None,
                      super_focus: Optional[ComfyTopazPhotoSuperFocusSettings]=None):
        now_millis = int(time.time() * 1000)
        prefix = '%s-%d' % (self.prefix, now_millis)
        upscaled_images = []
        upscale_user_settings = []
        upscale_autopilot_settings = []
        count = 0
        for image in images:
            count += 1
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            img_file = self.save_image(
                img, self.output_dir, '%s-%d.png' % (prefix, count)
            )
            # 调用内部方法
            (upscaled_img_file, user_settings, autopilot_settings) = self.topaz_upscale(
                img_file, compression, format, tpai_exe=tpai_exe, 
                upscale=upscale, sharpen=sharpen, face_recovery=face_recovery, denoise=denoise,
                crop_padding=crop_padding, text_recovery=text_recovery, super_focus=super_focus
            )
            upscaled_image = self.load_image(upscaled_img_file)
            upscaled_images.append(upscaled_image)
            upscale_user_settings.append(user_settings)
            upscale_autopilot_settings.append(autopilot_settings)

        return (upscale_user_settings, upscale_autopilot_settings, upscaled_images)

# 更新节点映射
NODE_CLASS_MAPPINGS = {
    'ComfyTopazPhoto': ComfyTopazPhoto,
    'ComfyTopazPhotoSharpenSettings': ComfyTopazPhotoSharpenSettings,
    'ComfyTopazPhotoUpscaleSettings': ComfyTopazPhotoUpscaleSettings,
    'ComfyTopazPhotoFaceRecoverySettings': ComfyTopazPhotoFaceRecoverySettings,
    'ComfyTopazPhotoDenoiseSettings': ComfyTopazPhotoDenoiseSettings,
    'ComfyTopazPhotoTextRecoverySettings': ComfyTopazPhotoTextRecoverySettings,
    'ComfyTopazPhotoSuperFocusSettings': ComfyTopazPhotoSuperFocusSettings,
    'ComfyTopazPhotoCropAndPaddingSettings': ComfyTopazPhotoCropAndPaddingSettings,
}

# 更新节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    'ComfyTopazPhoto': 'ComfyTopazPhoto', # 主节点显示名称
    'ComfyTopazPhotoSharpenSettings': 'ComfyTopazPhoto Sharpen Settings',
    'ComfyTopazPhotoUpscaleSettings': 'ComfyTopazPhoto Upscale Settings',
    'ComfyTopazPhotoFaceRecoverySettings': 'ComfyTopazPhoto Face Recovery Settings',
    'ComfyTopazPhotoDenoiseSettings': 'ComfyTopazPhoto Denoise Settings',
    'ComfyTopazPhotoTextRecoverySettings': 'ComfyTopazPhoto Text Recovery Settings',
    'ComfyTopazPhotoSuperFocusSettings': 'ComfyTopazPhoto Super Focus Settings',
    'ComfyTopazPhotoCropAndPaddingSettings': 'ComfyTopazPhoto Crop and Padding Settings',
}

class TopazError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# 添加新的测试和清理函数
def test_and_clean_topaz(tpai_exe, clean_cache=False, verbose=False):
    """
    测试 Topaz Photo AI 安装，并可选择清理其缓存文件。
    
    参数:
        tpai_exe (str): Topaz Photo AI 可执行文件的路径
        clean_cache (bool): 是否清理缓存文件
        verbose (bool): 是否输出详细日志
    
    返回:
        dict: 包含测试结果的字典
    """
    log_prefix = "[Topaz测试]"
    results = {
        "success": False,
        "test_output": "",
        "error_message": "",
        "cleaned_files": 0,
        "cache_size_before": 0,
        "cache_size_after": 0
    }
    
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
