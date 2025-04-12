import os
import numpy as np
import torch
import json
import subprocess
import tempfile
import time
from PIL import Image
import folder_paths # Ensure this import is correct and folder_paths is accessible
import shutil # Added for fallback copy

# Simplified Upscale Settings Node
class ComfyTopazPhotoUpscaleSettings:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("TOPAZ_UPSCALESETTINGS",)
    FUNCTION = "get_settings"
    CATEGORY = "ComfyTopazPhoto"

    def get_settings(self, enabled):
        # Returns only enable status and module name
        settings = {
            "enabled": enabled,
            "module": "enhance", # Use Topaz Enhance module
        }
        return (settings,)

# Simplified Sharpen Settings Node
class ComfyTopazPhotoSharpenSettings:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("TOPAZ_SHARPENSETTINGS",)
    FUNCTION = "get_settings"
    CATEGORY = "ComfyTopazPhoto"

    def get_settings(self, enabled):
        # Returns only enable status and module name
        settings = {
            "enabled": enabled,
            "module": "sharpen",
        }
        return (settings,)

# Simplified Face Recovery Settings Node
class ComfyTopazPhotoFaceRecoverySettings:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("TOPAZ_FACERECOVERYSETTINGS",)
    FUNCTION = "get_settings"
    CATEGORY = "ComfyTopazPhoto"

    def get_settings(self, enabled):
        # Returns only enable status and guessed module name
        settings = {
            "enabled": enabled,
            "module": "faceRecover", # Module name remains a guess
        }
        return (settings,)

# Main Node
class ComfyTopazPhoto:
    def __init__(self):
        # Ensure temporary directory exists
        self.output_dir = folder_paths.get_temp_directory()
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.type = "temp"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "tpai_exe": ("STRING", {"default": ""}),
                "compression": ("INT", {"default": 2, "min": 0, "max": 10}),
            },
            "optional": {
                "upscale": ("TOPAZ_UPSCALESETTINGS",),
                "sharpen": ("TOPAZ_SHARPENSETTINGS",),
                "face_recovery": ("TOPAZ_FACERECOVERYSETTINGS",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    FUNCTION = "process"
    CATEGORY = "ComfyTopazPhoto"

    def process(self, images, tpai_exe, compression, upscale=None, sharpen=None, face_recovery=None):
        if not tpai_exe or not os.path.exists(tpai_exe):
            raise ValueError("[ComfyTopazPhoto] Error: tpai.exe path is not valid or not provided.")

        batch_results = []
        autopilot_settings_str = "N/A"
        final_settings_json = "{}" # Default empty JSON

        for i, image in enumerate(images):
            input_path = None # Initialize paths
            output_path = None
            process = None # Initialize process variable
            filters = {} # Reset filters for each image

            try:
                # Convert tensor to PIL
                img_np = image.cpu().numpy()
                img_pil = Image.fromarray((img_np * 255).astype(np.uint8))

                # Create temp input file using tempfile for unique names
                with tempfile.NamedTemporaryFile(dir=self.output_dir, suffix=".png", delete=False) as temp_input_file:
                    input_path = temp_input_file.name
                # Ensure the file handle is closed before saving, or save directly
                img_pil.save(input_path, pnginfo=None, compress_level=6)

                # Create temp output file path
                temp_output_file = tempfile.NamedTemporaryFile(dir=self.output_dir, suffix=".png", delete=False)
                output_path = temp_output_file.name
                temp_output_file.close() # Close handle immediately

                # Build filters JSON (Simplified logic)
                if upscale and upscale.get("enabled", False):
                    filters[upscale.get("module", "enhance")] = {} # Use Autopilot settings
                if sharpen and sharpen.get("enabled", False):
                    filters[sharpen.get("module", "sharpen")] = {} # Use Autopilot settings
                if face_recovery and face_recovery.get("enabled", False):
                    filters[face_recovery.get("module", "faceRecover")] = {} # Use Autopilot settings

                # --- Processing Logic ---
                settings_json_for_run = "{}"
                if not filters:
                    # No filters enabled, copy original image to output path
                    print(f"[ComfyTopazPhoto] Warning: No Topaz filters enabled for image {i+1}. Returning original image.")
                    try:
                        if os.path.exists(output_path): os.remove(output_path)
                        # Use copy instead of link for reliability
                        shutil.copy2(input_path, output_path)
                    except Exception as e:
                        print(f"[ComfyTopazPhoto] Error copying original image: {e}")
                        raise RuntimeError(f"Failed to prepare original image for output: {e}")
                else:
                    # Filters enabled, run tpai.exe
                    settings_json_for_run = json.dumps({"filters": filters})
                    if i == 0: final_settings_json = settings_json_for_run # Store JSON for the first processed image

                    # Build command, ensure paths are quoted
                    command_parts = [
                        f'"{tpai_exe}"', # Assume tpai_exe might need quotes
                        f'"{input_path}"',
                        '--output', f'"{output_path}"',
                        '--compression', str(compression),
                        '--override',
                        '--settings', settings_json_for_run # Pass JSON string directly
                    ]
                    command_str = " ".join(command_parts)
                    print(f"[ComfyTopazPhoto] Executing: {command_str}")

                    startupinfo = None
                    if os.name == 'nt':
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    process = subprocess.Popen(command_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, text=True, encoding='utf-8', errors='replace')
                    stdout, stderr = process.communicate()
                    return_code = process.returncode

                    print(f"[ComfyTopazPhoto] stdout:\n{stdout}")
                    if stderr: print(f"[ComfyTopazPhoto] stderr:\n{stderr}")
                    print(f"[ComfyTopazPhoto] Return code: {return_code}")

                    # Extract Autopilot settings from stdout
                    for line in stdout.splitlines():
                        if line.startswith('Autopilot settings: '):
                            autopilot_settings_str = line.split('Autopilot settings: ', 1)[1]
                            break

                    # Check for errors
                    if return_code != 0 and return_code != 1: # 0=Success, 1=Partial success
                        error_message = f"tpai.exe failed with return code {return_code}. "
                        error_codes = {255: "No valid files passed.", 254: "Invalid log token. Login via GUI.", 253: "Invalid argument."}
                        error_message += error_codes.get(return_code, "Check console/logs.")
                        raise RuntimeError(f"[ComfyTopazPhoto] Error: {error_message}")

                    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                        raise RuntimeError(f"[ComfyTopazPhoto] Error: Output file missing or empty: {output_path}")

                # --- Load Output Image ---
                img_out_pil = Image.open(output_path).convert("RGB")
                img_out_np = np.array(img_out_pil).astype(np.float32) / 255.0
                img_out_tensor = torch.from_numpy(img_out_np).unsqueeze(0)
                batch_results.append(img_out_tensor)

            except Exception as e:
                 print(f"[ComfyTopazPhoto] Error processing image {i+1} ({input_path if input_path else 'N/A'}): {e}")
                 # Stop the batch on first error
                 raise RuntimeError(f"Error processing image {i+1}: {e}") from e
            finally:
                # --- Cleanup --- Ensures temp files are removed ---
                if process and process.poll() is None:
                    try: process.kill()
                    except Exception: pass
                if input_path and os.path.exists(input_path):
                    try: os.remove(input_path)
                    except OSError as e: print(f"Error removing temp input file {input_path}: {e}")
                if output_path and os.path.exists(output_path):
                    try: os.remove(output_path)
                    except OSError as e: print(f"Error removing temp output file {output_path}: {e}")

        # --- Final Check and Return ---
        if not batch_results:
             # This case should ideally be caught earlier if copy/processing fails
             raise RuntimeError("[ComfyTopazPhoto] Error: No images were successfully processed or prepared.")

        output_images = torch.cat(batch_results, dim=0)
        return (output_images, final_settings_json, autopilot_settings_str) 