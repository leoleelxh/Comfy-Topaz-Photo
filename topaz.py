import numpy as np
import os
import pprint
import time
import folder_paths
import torch
import subprocess
import json

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
        
        # 准备参数
        target_dir = os.path.join(self.output_dir, self.subfolder)
        
        # 新方法：将tpai_exe与其他参数分开处理
        exe_path = tpai_exe  # 保存可执行文件路径
        cmd_args = [
            '--output',        # output directory
            target_dir,
            '--compression',   # compression=[0,10] (default=2)
            str(compression),
            '--format',        # output format (omit to preserve original)
            format,
            '--showSettings',  # Prints out the final settings used when processing.
        ]
        
        # 检查是否有任何启用的手动设置
        has_manual_settings = (upscale and upscale.enabled) or (sharpen and sharpen.enabled) or \
                            (face_recovery and face_recovery.enabled) or (denoise and denoise.enabled) or \
                            (crop_padding and crop_padding.enabled) or (text_recovery and text_recovery.enabled) or \
                            (super_focus and super_focus.enabled)
        
        # 如果有手动设置，添加 --override 标志
        if has_manual_settings:
            print(f'{log_prefix} Adding --override flag because manual settings are provided.')
            cmd_args.append('--override')

        # 处理Upscale设置
        if upscale:
            print(f'{log_prefix} upscaler settings provided:', pprint.pformat(upscale.__dict__))
            # 只在启用时添加主标志和参数
            if upscale.enabled:
                print(f'{log_prefix} Enabling --upscale with model and parameters.')
                cmd_args.append('--upscale')
                
                # 必要参数 - 模型
                # 保持模型名称与用户选择一致 - 不自动添加前缀
                model_name = upscale.model
                
                # 输出更多模型调试信息
                print(f'{log_prefix} 尝试使用的模型名称: {model_name}')
                print(f'{log_prefix} 这应与 Topaz Photo AI 界面中显示的模型名称完全一致')
                
                # 使用原始模型名称，不添加前缀
                cmd_args.append(f'model={model_name}')
                
                # 可选参数 - 基础参数
                if hasattr(upscale, 'param1'):
                    cmd_args.append(f'param1={upscale.param1}')
                if hasattr(upscale, 'param2'):
                    cmd_args.append(f'param2={upscale.param2}')
                if hasattr(upscale, 'param3'):
                    cmd_args.append(f'param3={upscale.param3}')
                
                # 可选参数 - 高级参数
                if hasattr(upscale, 'mode'):
                    cmd_args.append(f'mode={upscale.mode}')
                if hasattr(upscale, 'resolution'):
                    cmd_args.append(f'resolution={upscale.resolution}')
                if hasattr(upscale, 'resolution_unit'):
                    cmd_args.append(f'resolutionUnit={upscale.resolution_unit}')
                if hasattr(upscale, 'locked'):
                    cmd_args.append(f'locked={str(upscale.locked).lower()}')
        
        # 处理Sharpen设置
        if sharpen:
            print(f'{log_prefix} sharpen settings provided:', pprint.pformat(sharpen.__dict__))
            # 只在启用时添加主标志和参数
            if sharpen.enabled:
                print(f'{log_prefix} Enabling --sharpen with model and parameters.')
                cmd_args.append('--sharpen')
                
                # 必要参数 - 模型
                # 确保Sharpen模型名称正确
                model_name = sharpen.model
                if not model_name.startswith('Sharpen '):
                    model_name = f'Sharpen {model_name}'
                cmd_args.append(f'model={model_name}')
                
                # 可选参数 - 基础参数
                if hasattr(sharpen, 'param1'):
                    cmd_args.append(f'param1={sharpen.param1}')  # strength
                if hasattr(sharpen, 'param2'):
                    cmd_args.append(f'param2={sharpen.param2}')  # denoise
                
                # 可选参数 - 高级参数
                if hasattr(sharpen, 'compression'):
                    cmd_args.append(f'compression={sharpen.compression}')
                if hasattr(sharpen, 'is_lens'):
                    cmd_args.append(f'isLens={str(sharpen.is_lens).lower()}')
                if hasattr(sharpen, 'auto'):
                    cmd_args.append(f'auto={str(sharpen.auto).lower()}')
                if hasattr(sharpen, 'mask'):
                    cmd_args.append(f'mask={str(sharpen.mask).lower()}')
                if hasattr(sharpen, 'locked'):
                    cmd_args.append(f'locked={str(sharpen.locked).lower()}')
        
        # 处理Face Recovery设置
        if face_recovery:
            print(f'{log_prefix} face recovery settings provided:', pprint.pformat(face_recovery.__dict__))
            # 只在启用时添加face标志和参数
            if face_recovery.enabled:
                print(f'{log_prefix} Enabling --face with model and parameters.')
                cmd_args.append('--face')
                
                # 必要参数 - 模型
                cmd_args.append(f'model={face_recovery.model}')
                
                # 可选参数 - 基础参数
                if hasattr(face_recovery, 'param1'):
                    cmd_args.append(f'param1={face_recovery.param1}')  # strength
                
                # 可选参数 - 高级参数
                if hasattr(face_recovery, 'version'):
                    cmd_args.append(f'version={face_recovery.version}')
                if hasattr(face_recovery, 'face_option'):
                    cmd_args.append(f'faceOption={face_recovery.face_option}')
                if hasattr(face_recovery, 'creativity'):
                    cmd_args.append(f'creativity={face_recovery.creativity}')
                if hasattr(face_recovery, 'locked'):
                    cmd_args.append(f'locked={str(face_recovery.locked).lower()}')
                
                # 面部部分
                if hasattr(face_recovery, 'face_parts') and face_recovery.face_parts:
                    face_parts_json = json.dumps(face_recovery.face_parts)
                    cmd_args.append(f'faceParts={face_parts_json}')
        
        # 添加处理Denoise设置的代码块
        if denoise:
            print(f'{log_prefix} denoise settings provided:', pprint.pformat(denoise.__dict__))
            # 只在启用时添加主标志和参数
            if denoise.enabled:
                print(f'{log_prefix} Enabling --denoise with model and parameters.')
                cmd_args.append('--denoise')
                
                # 必要参数 - 模型
                cmd_args.append(f'model={denoise.model}')
                
                # 可选参数 - 基础参数
                if hasattr(denoise, 'param1'):
                    cmd_args.append(f'param1={denoise.param1}')  # strength
                if hasattr(denoise, 'param2'):
                    cmd_args.append(f'param2={denoise.param2}')  # minor deblur
                
                # 可选参数 - 高级参数
                if hasattr(denoise, 'original_detail'):
                    cmd_args.append(f'recover_detail={denoise.original_detail}')
                if hasattr(denoise, 'auto'):
                    cmd_args.append(f'auto={str(denoise.auto).lower()}')
                if hasattr(denoise, 'mask'):
                    cmd_args.append(f'mask={str(denoise.mask).lower()}')
                if hasattr(denoise, 'locked'):
                    cmd_args.append(f'locked={str(denoise.locked).lower()}')
        
        # 处理裁剪和填充设置
        if crop_padding:
            print(f'{log_prefix} crop and padding settings provided:', pprint.pformat(crop_padding.__dict__))
            # 只在启用时添加主标志和参数
            if crop_padding.enabled:
                print(f'{log_prefix} Enabling --crop and --pad with parameters.')
                cmd_args.append('--crop')
                cmd_args.append(f'cropLeft={crop_padding.crop_left}')
                cmd_args.append(f'cropTop={crop_padding.crop_top}')
                cmd_args.append(f'cropRight={crop_padding.crop_right}')
                cmd_args.append(f'cropBottom={crop_padding.crop_bottom}')
                cmd_args.append('--pad')
                cmd_args.append(f'padLeft={crop_padding.pad_left}')
                cmd_args.append(f'padTop={crop_padding.pad_top}')
                cmd_args.append(f'padRight={crop_padding.pad_right}')
                cmd_args.append(f'padBottom={crop_padding.pad_bottom}')
        
        # 处理 Text Recovery 设置
        if text_recovery:
            print(f'{log_prefix} text recovery settings provided:', pprint.pformat(text_recovery.__dict__))
            # 只在启用时添加主标志和参数
            if text_recovery.enabled:
                print(f'{log_prefix} Enabling --text with parameters.')
                cmd_args.append('--text')
                
                # 参数设置
                if hasattr(text_recovery, 'param1_normal'):
                    cmd_args.append(f'param1_normal={text_recovery.param1_normal}')
                if hasattr(text_recovery, 'param2_normal'):
                    cmd_args.append(f'param2_normal={text_recovery.param2_normal}')
                if hasattr(text_recovery, 'param3_normal'):
                    cmd_args.append(f'param3_normal={text_recovery.param3_normal}')
                if hasattr(text_recovery, 'param1_noisy'):
                    cmd_args.append(f'param1_noisy={text_recovery.param1_noisy}')
                if hasattr(text_recovery, 'param2_noisy'):
                    cmd_args.append(f'param2_noisy={text_recovery.param2_noisy}')
                if hasattr(text_recovery, 'param3_noisy'):
                    cmd_args.append(f'param3_noisy={text_recovery.param3_noisy}')
                if hasattr(text_recovery, 'param4'):
                    cmd_args.append(f'param4={text_recovery.param4}')
                
                # 高级设置
                if hasattr(text_recovery, 'auto'):
                    cmd_args.append(f'auto={str(text_recovery.auto).lower()}')
                if hasattr(text_recovery, 'locked'):
                    cmd_args.append(f'locked={str(text_recovery.locked).lower()}')
        
        # 处理 Super Focus 设置
        if super_focus:
            print(f'{log_prefix} super focus settings provided:', pprint.pformat(super_focus.__dict__))
            # 只在启用时添加主标志和参数
            if super_focus.enabled:
                print(f'{log_prefix} Enabling --superfocus with parameters.')
                cmd_args.append('--superfocus')
                
                # 参数设置
                if hasattr(super_focus, 'amount'):
                    cmd_args.append(f'superFocusStrength={super_focus.amount}')
                if hasattr(super_focus, 'radius'):
                    cmd_args.append(f'gamma={super_focus.radius}')
                
                # 高级设置
                if hasattr(super_focus, 'auto'):
                    cmd_args.append(f'auto={str(super_focus.auto).lower()}')
                if hasattr(super_focus, 'locked'):
                    cmd_args.append(f'locked={str(super_focus.locked).lower()}')
        
        cmd_args.append(img_file)
        print(f'{log_prefix} tpaie.exe 参数列表:', pprint.pformat(cmd_args))
        
        # 执行Topaz命令并处理输出
        try:
            # 正确处理包含空格的路径和参数
            cmd_parts = []
            cmd_parts.append(f'"{exe_path}"')  # 将 tpai.exe 路径用引号包裹
            
            # 添加其他参数，为包含空格的参数添加引号
            for arg in cmd_args:
                if ' ' in str(arg) and not (str(arg).startswith('"') and str(arg).endswith('"')):
                    cmd_parts.append(f'"{arg}"')
                else:
                    cmd_parts.append(str(arg))
            
            # 构建最终命令字符串
            cmd_str = ' '.join(cmd_parts)
            print(f'{log_prefix} 执行命令: {cmd_str}')
            
            # 使用 shell=True 可能有助于处理特殊字符和路径问题
            p_tpai = subprocess.run(cmd_str, capture_output=True, text=True, shell=True, encoding='utf-8', errors='ignore')
            print(f'{log_prefix} tpaie.exe return code:', p_tpai.returncode)
            print(f'{log_prefix} tpaie.exe STDOUT:', p_tpai.stdout)
            print(f'{log_prefix} tpaie.exe STDERR:', p_tpai.stderr)

            # 检查常见错误
            if "Error | AI Engine Load Exception: Could not load model" in p_tpai.stderr:
                error_message = "Topaz Photo AI failed to load the model. Please check if the model is installed correctly and the model name is valid."
                print(f'{log_prefix} {error_message}')
                
                # 更详细的模型名称提示
                if upscale and upscale.enabled:
                    original_model = upscale.model
                    print(f'{log_prefix} 尝试使用的 upscale 模型: {original_model}')
                    print(f'{log_prefix} 建议尝试以下模型名称变体:')
                    
                    # 提供不同的模型名称格式建议
                    model_variants = []
                    
                    # 1. 完全匹配 GUI 显示的原始名称
                    model_variants.append(original_model)
                    
                    # 2. 尝试不同的大小写版本
                    model_variants.append(original_model.lower())
                    model_variants.append(original_model.upper())
                    
                    # 3. 尝试无空格版本
                    model_variants.append(original_model.replace(" ", ""))
                    
                    # 4. 尝试常见标准模型名称
                    model_variants.append("Standard v2")
                    model_variants.append("Standard")
                    model_variants.append("Std v2")
                    
                    # 5. 尝试无前缀和有前缀版本
                    if original_model.startswith("Enhance "):
                        model_variants.append(original_model[8:])  # 去掉"Enhance "
                    else:
                        model_variants.append(f"Enhance {original_model}")
                    
                    # 6. 尝试图中显示的所有其他模型
                    for other_model in ["Standard v2", "Standard v1", "High fidelity v2", "High fidelity v1", "Low resolution", "Graphics"]:
                        if other_model != original_model and other_model not in model_variants:
                            model_variants.append(other_model)
                    
                    # 打印所有变体建议
                    print(f'{log_prefix} 建议尝试以下模型名称:')
                    for i, variant in enumerate(model_variants):
                        print(f'{log_prefix}   {i+1}. "{variant}"')
                    
                    print(f'{log_prefix} 请在 ComfyUI 中修改模型选择，尝试以上名称')
                    print(f'{log_prefix} 最好使用与 Topaz Photo AI 界面中完全一致的名称')
                    
                    print(f'{log_prefix} 其他解决方案:')
                    print(f'{log_prefix}   1. 打开 Topaz Photo AI GUI 应用，完成一次放大处理，然后关闭')
                    print(f'{log_prefix}   2. 确保 Topaz Photo AI 应用已完全关闭（检查系统托盘）')
                    print(f'{log_prefix}   3. 在 Topaz Photo AI 中选择另一个模型（如 "Standard v1" 或 "Graphics"）')
                    print(f'{log_prefix}   4. 检查模型是否已下载（在 Topaz Photo AI 设置中查看模型）')
                    print(f'{log_prefix}   5. 重新安装或更新 Topaz Photo AI 到最新版本')
                
                if sharpen and sharpen.enabled:
                    print(f'{log_prefix} 尝试使用的 sharpen 模型: {sharpen.model}')
                    print(f'{log_prefix} 请尝试以下名称变体:')
                    print(f'{log_prefix}   1. "Sharpen {sharpen.model.replace("Sharpen ", "")}"')
                    print(f'{log_prefix}   2. "{sharpen.model}"')
                    print(f'{log_prefix}   3. "Sharpen Standard V2" (默认模型)')
                
                # 检查是否可以直接运行 tpai.exe
                print(f'{log_prefix} 尝试直接使用以下命令测试 Topaz Photo AI:')
                test_cmd = f'{exe_path} --help'
                print(f'{log_prefix} > {test_cmd}')
                
                # 检查 Topaz 日志位置
                topaz_log_path = os.path.expanduser("~/AppData/Local/Topaz Labs LLC/Topaz Photo AI/Logs")
                print(f'{log_prefix} 请检查 Topaz Photo AI 日志以获取更多信息: {topaz_log_path}')
                
                # 后续解决方案建议
                print(f'{log_prefix} 如果问题仍然存在，您可以尝试:')
                print(f'{log_prefix}   1. 确保 Topaz Photo AI 应用程序处于关闭状态')
                print(f'{log_prefix}   2. 重新安装或更新 Topaz Photo AI')
                print(f'{log_prefix}   3. 将 upscale.model 设置为 "Enhance Standard V2"')
                print(f'{log_prefix}   4. 如果仍然不起作用，使用 Comfy 原生的放大节点作为替代')
                
                raise RuntimeError(error_message)

            user_settings, autopilot_settings = self.get_settings(p_tpai.stdout)

            output_filepath = os.path.join(target_dir, os.path.basename(img_file))
            if p_tpai.returncode != 0 or not os.path.exists(output_filepath):
                error_message = f"Topaz Photo AI execution failed with return code {p_tpai.returncode} or output file not found."
                if p_tpai.stderr:
                    error_message += f"\nSTDERR:\n{p_tpai.stderr}"
                # 更新错误信息来源
                print(f'{log_prefix} Raising error: {error_message}') 
                raise RuntimeError(error_message)
                
        except Exception as e:
            error_message = f"Error executing Topaz Photo AI: {str(e)}"
            print(f'{log_prefix} {error_message}')
            raise RuntimeError(error_message)

        return (output_filepath, user_settings, autopilot_settings)

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
