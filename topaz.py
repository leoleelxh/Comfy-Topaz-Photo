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

class TopazUpscaleSettings:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'enabled': (['true', 'false'], {'default': 'true'}),
                'model': ([
                    'Standard', 
                    'Standard V2', 
                    'High Fidelity', 
                    'High Fidelity V2', 
                    #'Graphics', what is this
                    'Low Resolution'
                ], {'default': 'Standard V2'}),
                'scale': ('FLOAT', {'default': 2.0, 'min': 0, 'max': 10, 'round': False, }),
                'denoise': ('FLOAT', {'default': 0.2, 'min': 0, 'max': 10, 'round': False, 'display': 'denoise (param1)'}),
                'deblur': ('FLOAT', {'default': 0.2, 'min': 0, 'max': 10, 'round': False, 'display': 'deblur (param2)'}),
                'detail': ('FLOAT', {'default': 0.2, 'min': 0, 'max': 10, 'round': False, 'display': 'detail (param3)'}),
            },
            'optional': {

            },
        }

    RETURN_TYPES = ('TopazUpscaleSettings',)
    RETURN_NAMES = ('upscale_settings',)
    FUNCTION = 'init'
    CATEGORY = 'image'
    OUTPUT_NODE = False
    OUTPUT_IS_LIST = (False,)
    
    def init(self, enabled, model, scale, denoise, deblur, detail):
        self.enabled = str(True).lower() == enabled.lower()
        self.model = model
        self.scale = scale
        self.denoise = denoise
        self.deblur = deblur
        self.detail = detail
        return (self,)

class TopazSharpenSettings:       
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'enabled': (['true', 'false'], {'default': 'true'}),
                'model': ([
                    'Standard', 
                    'Strong', 
                    # TODO: why don't these work?
                    #'Lens Blur', 
                    #'Motion Blur', 
                ], {'default': 'Standard'}),
                'compression': ('FLOAT', {'default': 0.5, 'min': 0, 'max': 1, 'round': 0.01,}),
                'is_lens': (['true', 'false'], {'default': 'false'}),
                'lensblur': ('FLOAT', {'default': 0.0, 'min': 0, 'max': 10, 'round': False,}),
                'mask': (['true', 'false'], {'default': 'false'}),
                'motionblur': ('FLOAT', {'default': 0.0, 'min': 0, 'max': 10, 'round': False,}),
                'noise': ('FLOAT', {'default': 0.0, 'min': 0, 'max': 10, 'round': False,}),
                'strength': ('FLOAT', {'default': 0.0, 'min': 0, 'max': 10, 'round': False, 'display': 'strength (param1)'}), # TODO: why doesn't "display" work?
                'denoise': ('FLOAT', {'default': 0.0, 'min': 0, 'max': 10, 'round': False, "display": 'denoise (param2)'}),   # param2 (Lens/Motion Blur only)
            },
            'optional': {
                
            },
        }

    RETURN_TYPES = ('TopazSharpenSettings',)
    RETURN_NAMES = ('sharpen_settings',)
    FUNCTION = 'init'
    CATEGORY = 'image'
    OUTPUT_IS_LIST = (False,)
    
    def init(self, enabled, model, compression, is_lens, lensblur, mask, motionblur, noise, strength, denoise):
        self.enabled = str(True).lower() == enabled.lower()
        self.model = model
        self.compression = compression
        self.is_lens = is_lens
        self.lensblur = lensblur
        self.mask = mask
        self.motionblur = motionblur
        self.noise = noise
        self.strength = strength
        self.denoise = denoise
        return (self,)

class TopazPhotoAI:
    '''
    A node that uses Topaz Image AI (tpai.exe) behind the scenes to enhance (upscale/sharpen/denoise/etc.) the given image(s).
    
    If no settings are provided, auto-detected (auto-pilot) settings are used.
    '''
    def __init__(self):
        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        self.comfy_dir = os.path.abspath(os.path.join(self.this_dir, '..', '..'))
        self.subfolder = 'upscaled'
        self.output_dir = os.path.join(self.comfy_dir, 'temp')
        self.prefix = 'tpai'
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
                # 'blur_level': ('FLOAT', {'default': -1, 'min': -10, 'max': 10}),
                # 'noise_level': ('FLOAT', {'default': -1, 'min': -10, 'max': 10}),
                'upscale': ('TopazUpscaleSettings',),
                'sharpen': ('TopazSharpenSettings',),
            },
            "hidden": {
            }
        }

    RETURN_TYPES = ('STRING', 'STRING', 'IMAGE')
    RETURN_NAMES = ('settings', 'autopilot_settings', 'IMAGE')
    FUNCTION = 'upscale_image'
    CATEGORY = 'image'
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
        '''
        Extracts the settings JSON string from the stdout of the tpai.exe process
        '''
        if not stdout:
            print('\033[31mComfy-Topaz:\033[0m Warning: Received empty stdout for get_settings.')
            return '{}', '{}'

        settings_json = '{}'
        autopilot_settings_json = '{}'
        try:
            settings_start_marker = 'Final Settings for'
            settings_start = stdout.find(settings_start_marker)

            if settings_start == -1:
                print(f'\033[31mComfy-Topaz:\033[0m Warning: "{settings_start_marker}" not found in stdout. Cannot extract settings.')
                print(f'\033[31mComfy-Topaz:\033[0m Full stdout was:\n{stdout}')
                return '{}', '{}'

            settings_start = stdout.find('{', settings_start)

            if settings_start == -1:
                print('\033[31mComfy-Topaz:\033[0m Warning: Could not find opening brace \'{\' after settings marker.')
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
                print('\033[31mComfy-Topaz:\033[0m Warning: Could not find matching closing brace \'}\' for settings JSON.')
                return '{}', '{}'

            settings_json_str = str(stdout[settings_start : settings_end + 1])

            settings = json.loads(settings_json_str)
            autopilot_settings = settings.pop('autoPilotSettings', {})
            user_settings_json = json.dumps(settings, indent=2).replace('"', "'")
            autopilot_settings_json = json.dumps(autopilot_settings, indent=2).replace('"', "'")

        except json.JSONDecodeError as e:
            print(f'\033[31mComfy-Topaz:\033[0m Error decoding settings JSON: {e}')
            print(f'\033[31mComfy-Topaz:\033[0m Extracted string was: {settings_json_str}')
            return '{}', '{}'
        except Exception as e:
            print(f'\033[31mComfy-Topaz:\033[0m An unexpected error occurred in get_settings: {e}')
            print(f'\033[31mComfy-Topaz:\033[0m Full stdout was:\n{stdout}')
            return '{}', '{}'

        return user_settings_json, autopilot_settings_json

    def topaz_upscale(self, img_file, compression=0, format='png', tpai_exe=None, 
                      upscale: Optional[TopazUpscaleSettings]=None, 
                      sharpen: Optional[TopazSharpenSettings]=None):
        if not os.path.exists(tpai_exe):
            raise ValueError('Topaz AI Upscaler not found at %s' % tpai_exe)
        if compression < 0 or compression > 10:
            raise ValueError('compression must be between 0 and 10')        
        
        target_dir = os.path.join(self.output_dir, self.subfolder)
        tpai_args = [
            tpai_exe,
            '--output',        # output directory
            target_dir,
            '--compression',   # compression=[0,10] (default=2)
            str(compression),
            '--format',        # output format (omit to preserve original)
            format,
            '--showSettings',  # Prints out the final settings used when processing.
        ]
        
        # 检查是否有任何启用的手动设置
        has_manual_settings = (upscale and upscale.enabled) or (sharpen and sharpen.enabled)
        
        # 如果有手动设置，添加 --override 标志
        if has_manual_settings:
            print('\033[31mComfy-Topaz:\033[0m Adding --override flag because manual settings are provided.')
            tpai_args.append('--override')

        if upscale:
            print('\033[31mComfy-Topaz:\033[0m upscaler settings provided:', pprint.pformat(upscale))
            # 只在启用时添加主标志，并传递 model 参数
            if upscale.enabled:
                print('\033[31mComfy-Topaz:\033[0m Enabling --upscale and specifying model.')
                tpai_args.append('--upscale')
                # 只传递 model 参数
                tpai_args.append(f'model={upscale.model}')
            # 注释掉传递其他子参数的代码
            # if upscale.enabled:
            #     tpai_args.append(f'scale={upscale.scale}')
            #     tpai_args.append(f'param1={upscale.denoise}') # Minor Denoise
            #     tpai_args.append(f'param2={upscale.deblur}')  # Minor Deblur
            #     tpai_args.append(f'param3={upscale.detail}')  # Fix Compression
            #     # tpai_args.append(f'model={upscale.model}') # 已移到上面
            # else:
            #     pass 
                
            
        if sharpen:
            print('\033[31mComfy-Topaz:\033[0m sharpen settings provided:', pprint.pformat(sharpen))
             # 只在启用时添加主标志，并传递 model 参数
            if sharpen.enabled:
                print('\033[31mComfy-Topaz:\033[0m Enabling --sharpen and specifying model.')
                tpai_args.append('--sharpen')
                # 只传递 model 参数 (注意 Sharpen 模型名称可能需要前缀)
                tpai_args.append(f'model=Sharpen {sharpen.model}')
            # 注释掉传递其他子参数的代码
            # if sharpen.enabled:
            #     # tpai_args.append(f'model=Sharpen {sharpen.model}') # 已移到上面
            #     tpai_args.append(f'compression={sharpen.compression}')
            #     tpai_args.append(f'is_lens={str(sharpen.is_lens).lower()}')
            #     tpai_args.append(f'lensblur={sharpen.lensblur}')
            #     tpai_args.append(f'mask={str(sharpen.mask).lower()}')
            #     tpai_args.append(f'motionblur={sharpen.motionblur}')
            #     tpai_args.append(f'noise={sharpen.noise}')
            #     tpai_args.append(f'param1={sharpen.strength}')
            #     tpai_args.append(f'param2={sharpen.denoise}')
            # else:
            #     pass
            
        tpai_args.append(img_file)
        print('\033[31mComfy-Topaz:\033[0m tpaie.exe args:', pprint.pformat(tpai_args))
        p_tpai = subprocess.run(tpai_args, capture_output=True, text=True, shell=False, encoding='utf-8', errors='ignore')
        print('\033[31mComfy-Topaz:\033[0m tpaie.exe return code:', p_tpai.returncode)
        print('\033[31mComfy-Topaz:\033[0m tpaie.exe STDOUT:', p_tpai.stdout)
        print('\033[31mComfy-Topaz:\033[0m tpaie.exe STDERR:', p_tpai.stderr)

        user_settings, autopilot_settings = self.get_settings(p_tpai.stdout)

        output_filepath = os.path.join(target_dir, os.path.basename(img_file))
        if p_tpai.returncode != 0 or not os.path.exists(output_filepath):
            error_message = f"Topaz Photo AI execution failed with return code {p_tpai.returncode} or output file not found."
            if p_tpai.stderr:
                error_message += f"\nSTDERR:\n{p_tpai.stderr}"
            raise RuntimeError(error_message)

        return (output_filepath, user_settings, autopilot_settings)

    def upscale_image(self, images, compression=0, format='png', tpai_exe=None, 
                      upscale: Optional[TopazUpscaleSettings]=None, 
                      sharpen: Optional[TopazSharpenSettings]=None):
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
            (upscaled_img_file, user_settings, autopilot_settings) = self.topaz_upscale(img_file, compression, format, tpai_exe=tpai_exe, upscale=upscale, sharpen=sharpen)
            upscaled_image = self.load_image(upscaled_img_file)
            upscaled_images.append(upscaled_image)
            upscale_user_settings.append(user_settings)
            upscale_autopilot_settings.append(autopilot_settings)

        return (upscale_user_settings, upscale_autopilot_settings, upscaled_images)

NODE_CLASS_MAPPINGS = {
    'TopazPhotoAI': TopazPhotoAI,
    'TopazSharpenSettings': TopazSharpenSettings,
    'TopazUpscaleSettings': TopazUpscaleSettings,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    'TopazPhotoAI': 'Topaz Photo AI',
    'TopazSharpenSettings': 'Topaz Sharpen Settings',
    'TopazUpscaleSettings': 'Topaz Upscale Settings',
}
