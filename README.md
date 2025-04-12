# ComfyUI Node for Topaz Photo AI (`ComfyTopazPhoto`)

Integrate Topaz Photo AI's powerful image enhancement capabilities directly into your ComfyUI workflows.

This node allows you to call the `tpai.exe` command-line interface from within ComfyUI to upscale, sharpen, denoise, and apply other adjustments offered by Topaz Photo AI.

**Note:** This node is based on the work of [choey/Comfy-Topaz](https://github.com/choey/Comfy-Topaz) and has been adapted and debugged for compatibility with newer versions of Topaz Photo AI.

## Requirements

*   **Licensed installation of Topaz Photo AI:** This node requires a working installation of Topaz Photo AI, specifically the `tpai.exe` executable.
*   **Topaz Photo AI Models:** Ensure that Topaz Photo AI has successfully downloaded the necessary AI models. You can usually verify this by running the main Topaz Photo AI application.

## Installation

1.  Clone this repository into your `ComfyUI/custom_nodes/` directory:
    ```bash
    git clone <your-repo-url> ComfyUI/custom_nodes/ComfyTopazPhoto
    ```
    (Replace `<your-repo-url>` with the actual URL of this repository)
2.  Alternatively, download the repository contents as a ZIP file and extract it into `ComfyUI/custom_nodes/ComfyTopazPhoto`.
3.  **Restart ComfyUI.**

## Usage

**⚠️ CRITICAL UPSCALING REQUIREMENT ⚠️**

The upscale factor (`scale`) for Topaz Photo AI **cannot be controlled** from within ComfyUI using this node. You **must** set your desired upscale factor directly in the Topaz Photo AI application settings under **Preferences -> Autopilot -> Upscale & Resize**. The corresponding input for `scale` **is not available** on the `ComfyTopazPhoto Upscale Settings` node because it would be **ignored** by the application.

**Note:** Even when you manually specify other upscaling parameters through the settings node, the upscale factor will always be determined by what you've set in the Topaz Photo AI GUI. This is a limitation of the `tpai.exe` command-line interface, not of this ComfyUI node.

After installation, you will find the following nodes under the `ComfyTopazPhoto` category:

*   **`ComfyTopazPhoto` (Main Node):** This is the core node that executes Topaz Photo AI.
*   **`ComfyTopazPhoto Upscale Settings`:** Connect this node to the `upscale` input of the main node to enable and partially control upscaling.
*   **`ComfyTopazPhoto Sharpen Settings`:** Connect this node to the `sharpen` input of the main node to enable and partially control sharpening.

### Inputs (Main Node)

*   `images`: The input image(s) to process.
*   `tpai_exe`: **Required.** The full path to your `tpai.exe` executable (e.g., `H:\\Program Files\\Topaz Labs LLC\\Topaz Photo AI\\tpai.exe`).
*   `compression`: PNG compression level (0-10, default: 2).
*   `upscale`: (Optional) Connect the output of the `ComfyTopazPhoto Upscale Settings` node here.
*   `sharpen`: (Optional) Connect the output of the `ComfyTopazPhoto Sharpen Settings` node here.

### Inputs (Settings Nodes - Upscale & Sharpen)

*   `enabled`: Set to `true` to enable this enhancement (Upscale or Sharpen).
*   `model`: Select the specific AI model to use for the enhancement. **This parameter should be correctly passed to `tpai.exe`.**
*   **Upscale Parameters:**
    *   **⚠️ IMPORTANT:** The `scale` parameter is **NOT available** on this node. The upscale factor is determined **exclusively** by the settings in the Topaz Photo AI GUI under **Preferences -> Autopilot -> Upscale & Resize**. You **must** configure this setting in the GUI before using this node for upscaling.
    *   `denoise` (param1), `deblur` (param2), `detail` (param3): These parameters **should** be correctly passed to `tpai.exe` and override the defaults when Upscale is enabled.
*   **Sharpen Parameters:**
    *   `strength` (param1), `denoise` (param2), `compression`, `is_lens`, etc.: Similar to upscale, it's highly likely that only the `model` parameter is reliably passed via CLI due to `tpai.exe` limitations. Other parameters are likely ignored, and Topaz Photo AI's defaults will be used. (Further testing needed if specific sharpen parameters are critical).

### Outputs (Main Node)

*   `IMAGE`: The processed image(s).
*   `settings`: A string containing the final JSON settings used by `tpai.exe` to process the image (excluding Autopilot settings, reflecting the parameters `tpai.exe` actually used).
*   `autopilot_settings`: A string containing the Autopilot settings detected by `tpai.exe`.

### Workflow Strategy

1.  **Set Fixed Upscale Factor in Topaz GUI:** *(Required step)* Open Topaz Photo AI, go to Preferences -> Autopilot -> Upscale & Resize, and set your desired **default** upscale factor (e.g., 2x, 4x). Save preferences. **This step cannot be skipped** if you want to control the upscale factor.
2.  **Use ComfyUI Node:**
    *   Connect the `ComfyTopazPhoto Upscale Settings` node if you want Topaz to perform upscaling (using the factor set in the GUI).
    *   Set `enabled` to `true`.
    *   Select the desired `model`.
    *   Adjust `denoise`, `deblur`, `detail` sliders as needed (these should work).
    *   Remember that the actual upscale factor is controlled by the Topaz GUI settings.
    *   Connect the main `ComfyTopazPhoto` node and provide the `tpai_exe` path.
3.  **For Variable Upscaling:** If you need different upscale factors within the *same* workflow, **do not** rely on the Topaz node for scaling. Instead:
    *   Use a standard ComfyUI upscale node (like `Image Upscale with Model` or `ImageScale`) *before* the `ComfyTopazPhoto` node to achieve the desired size.
    *   You can still use the `ComfyTopazPhoto` node afterward for other enhancements (like sharpening or applying denoise/deblur/detail via the Upscale node with `enabled=true` but knowing the scale factor comes from the GUI setting) or set `enabled=false` on the relevant Topaz setting node if you only want processing from other enabled Topaz modules.

![Simple Workflow Example](demo1.png) *(Screenshot might show older node names and functionality)*

## Current Limitations & Troubleshooting

*   **Upscale Factor Control:** The upscale factor (`scale`) **cannot** be controlled from this node. It **must** be preset in the Topaz Photo AI GUI preferences (Autopilot settings). **There is no workaround for this limitation** as it is inherent to how the `tpai.exe` command-line interface functions.
*   **Parameter Override Reliability:** Only the `model`, and potentially the `param1`/`param2`/`param3` for upscale, seem reliably passed via the CLI. Other specific parameters on the settings nodes are likely ignored due to `tpai.exe` limitations.
*   **`Could not load model` Error:** Likely an issue with the Topaz Photo AI installation or model files. Check the main app and Topaz logs (`AppData\Local\Topaz Labs LLC\Topaz Photo AI\Logs`).
*   **Initial Setup:** Ensure the `tpai_exe` path is correct.

## Future Development (TODO)

*   Monitor future `tpai.exe` versions for potential fixes or documented changes to CLI parameter handling.
*   Update documentation if Topaz Labs clarifies or fixes CLI parameter behavior.
*   Consider adding separate nodes for other CLI-controllable features if they prove reliable (e.g., Denoise module if its `strength`, `minor_deblur` etc. parameters work via CLI).

## Proposed Improvement

Based on code analysis, the current implementation can be simplified to make it more user-friendly. Since many of the parameters passed to `tpai.exe` are ignored or unreliable, we can streamline the nodes to focus only on enabling/disabling features:

### Suggested Changes:

1. **Simplify Settings Nodes**:
   * Replace all parameter inputs with just an `enabled` toggle
   * Remove confusing parameters that have no effect on the final output
   * The model selection can be kept as it seems to be reliably passed to `tpai.exe`

2. **Updated Code Example**:
   ```python
   # Simplified Upscale Settings Node
   class ComfyTopazPhotoUpscaleSettings:
       @classmethod
       def INPUT_TYPES(cls):
           return {
               'required': {
                   'enabled': ('BOOLEAN', {'default': False}),
                   'model': ([
                       'Standard', 
                       'Standard V2', 
                       'High Fidelity', 
                       'High Fidelity V2', 
                       'Low Resolution'
                   ], {'default': 'Standard V2'}),
               },
           }
       
       RETURN_TYPES = ('ComfyTopazPhotoUpscaleSettings',)
       FUNCTION = 'init'
       CATEGORY = 'ComfyTopazPhoto'
       
       def init(self, enabled, model):
           self.enabled = enabled
           self.model = model
           return (self,)
   ```

3. **Main Node Implementation**:
   * Keep the current command line argument structure
   * Remove parameter passing code except for the model selection
   * Use the Topaz Photo AI defaults for all other parameters, which will be controlled via the GUI settings

4. **User Experience Benefits**:
   * More intuitive interface
   * Less confusion about which parameters actually work
   * Clearer expectations about what settings need to be configured in the Topaz GUI
   * Simplified workflow with fewer potential errors

This approach would make the node much more straightforward to use - simply toggle 'enabled' for the features you want to use (upscale/sharpen), select a model, and let Topaz Photo AI's built-in settings handle the rest.

### Inputs (Settings Nodes - Simplified)

*   `enabled`: Boolean toggle to enable/disable this enhancement (Upscale or Sharpen).
*   `model`: Select the specific AI model to use for the enhancement. **This parameter should be correctly passed to `tpai.exe`.**

### Workflow Strategy (Simplified)

1. **Set Fixed Upscale Factor in Topaz GUI:** *(Required step)* Open Topaz Photo AI, go to Preferences -> Autopilot -> Upscale & Resize, and set your desired **default** upscale factor (e.g., 2x, 4x). Set other parameters like denoise, deblur, etc. as desired directly in the Topaz GUI.

2. **Use ComfyUI Node:**
   * Connect the `ComfyTopazPhoto Upscale Settings` node to the main node
   * Simply toggle `enabled` to `true` to activate upscaling
   * Select the desired `model`
   * Connect the main `ComfyTopazPhoto` node and provide the `tpai_exe` path

This simplified approach better reflects the actual capabilities of the `tpai.exe` command-line interface and provides a cleaner user experience.

## Implementation Status

✅ **Simplification Completed!**

The code has been updated to implement the simplified approach described above. The main changes include:

1. Simplified `ComfyTopazPhotoUpscaleSettings` and `ComfyTopazPhotoSharpenSettings` classes:
   * Removed all parameters except `enabled` and `model`
   * Simplified initialization methods

2. Modified `topaz_upscale` method:
   * Removed code that tried to pass parameters that were being ignored
   * Only passes the model selection which seems to be reliably handled by `tpai.exe`
   * Added better logging for clarity

### How to Use the Simplified Version

With this simplified implementation, your workflow becomes much more straightforward:

1. **Configure Topaz Photo AI GUI** - Set up all your preferred enhancement parameters (upscale factor, denoise strength, deblur, etc.) directly in the Topaz Photo AI application.

2. **In ComfyUI:**
   * Add the `ComfyTopazPhoto` main node
   * Add `ComfyTopazPhoto Upscale Settings` and/or `ComfyTopazPhoto Sharpen Settings` nodes
   * For each settings node, simply:
     * Set `enabled` to `true` for the features you want to use
     * Select the appropriate `model`
   * Connect these settings nodes to the main node
   * Connect your image source to the main node
   * Provide the path to `tpai.exe`

3. **Run Your Workflow** - The image will be processed according to:
   * The models you selected in ComfyUI
   * The parameters you configured in the Topaz Photo AI GUI

### Simplified Workflow Diagram

```
+----------------+
| Image Source   |
+--------+-------+
         |
         v
+--------+----------------+    +--------------------------------+
| ComfyTopazPhoto         |<---| ComfyTopazPhoto Upscale       |
| +------------------+    |    | +-------------------------+    |
| | images           |    |    | | enabled: true           |    |
| | tpai_exe: [path] |<---+----+ | model: Standard V2      |    |
| | upscale          |    |    | +-------------------------+    |
| | sharpen          |<---+    +--------------------------------+
| +------------------+    |    
|                         |    +--------------------------------+
+--------+----------------+    | ComfyTopazPhoto Sharpen       |
         |                     | +-------------------------+    |
         v                     | | enabled: false          |    |
+--------+-------+             | | model: Standard         |    |
| Output Image   |             | +-------------------------+    |
+----------------+             +--------------------------------+
```

This implementation acknowledges the limitations of the Topaz Photo AI command-line interface while providing a clean, intuitive way to leverage its powerful image enhancement capabilities within ComfyUI.

