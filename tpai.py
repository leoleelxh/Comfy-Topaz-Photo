class ComfyTopazPhotoUpscaleSettings:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
                "model": (['standard', 'high fidelity', 'graphics', 'low resolution'], ),
                # 'scale': ('FLOAT', {'default': 2.0, 'min': 1.0, 'max': 6.0, 'step': 0.1}), # Scale is controlled by GUI Autopilot
                "param1": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}), # Mapped to denoise?
                "param2": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}), # Mapped to deblur?
                "param3": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}), # Mapped to detail?
            }
        }

    RETURN_TYPES = ("TOPAZ_UPSCALESETTINGS",)
    FUNCTION = "get_settings"
    CATEGORY = "ComfyTopazPhoto"
    # NODE_DISPLAY_NAME = "Topaz Upscale Settings"

    def get_settings(self, enabled, model, param1, param2, param3):
        settings = {
            "enabled": enabled,
            "module": "enhance", # Keep enhance as module ID for upscale
            "model": model,
            # "scale": scale, # Removed
            "param1": param1, # Denoise
            "param2": param2, # Deblur
            "param3": param3, # Detail
        }
        return (settings,) 