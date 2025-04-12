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

**IMPORTANT NOTE ON UPSCALING:** The upscale factor (`scale`) for Topaz Photo AI **cannot be controlled** from within ComfyUI using this node. You **must** set your desired upscale factor directly in the Topaz Photo AI application settings under **Preferences -> Autopilot -> Upscale & Resize**. The corresponding input for `scale` **is not available** on the `ComfyTopazPhoto Upscale Settings` node because it would be **ignored** by the application.

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
    *   `scale`: **IMPORTANT LIMITATION:** The `tpai.exe` command-line interface **does not** accept a scale factor parameter. The actual upscale factor used is determined **solely** by the settings configured in the **Topaz Photo AI GUI** under **Preferences -> Autopilot -> Upscale & Resize**. Therefore, there is **no `scale` input** on this node. You **must** set your desired **fixed** upscale factor in the Topaz Photo AI application preferences.
    *   `denoise` (param1), `deblur` (param2), `detail` (param3): These parameters **should** be correctly passed to `tpai.exe` and override the defaults when Upscale is enabled.
*   **Sharpen Parameters:**
    *   `strength` (param1), `denoise` (param2), `compression`, `is_lens`, etc.: Similar to upscale, it's highly likely that only the `model` parameter is reliably passed via CLI due to `tpai.exe` limitations. Other parameters are likely ignored, and Topaz Photo AI's defaults will be used. (Further testing needed if specific sharpen parameters are critical).

### Outputs (Main Node)

*   `IMAGE`: The processed image(s).
*   `settings`: A string containing the final JSON settings used by `tpai.exe` to process the image (excluding Autopilot settings, reflecting the parameters `tpai.exe` actually used).
*   `autopilot_settings`: A string containing the Autopilot settings detected by `tpai.exe`.

### Workflow Strategy

1.  **Set Fixed Upscale Factor in Topaz GUI:** Open Topaz Photo AI, go to Preferences -> Autopilot -> Upscale & Resize, and set your desired **default** upscale factor (e.g., 2x, 4x). Save preferences.
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

*   **Upscale Factor Control:** The upscale factor (`scale`) **cannot** be controlled from this node. It **must** be preset in the Topaz Photo AI GUI preferences (Autopilot settings).
*   **Parameter Override Reliability:** Only the `model`, and potentially the `param1`/`param2`/`param3` for upscale, seem reliably passed via the CLI. Other specific parameters on the settings nodes are likely ignored due to `tpai.exe` limitations.
*   **`Could not load model` Error:** Likely an issue with the Topaz Photo AI installation or model files. Check the main app and Topaz logs (`AppData\Local\Topaz Labs LLC\Topaz Photo AI\Logs`).
*   **Initial Setup:** Ensure the `tpai_exe` path is correct.

## Future Development (TODO)

*   Monitor future `tpai.exe` versions for potential fixes or documented changes to CLI parameter handling.
*   Update documentation if Topaz Labs clarifies or fixes CLI parameter behavior.
*   Consider adding separate nodes for other CLI-controllable features if they prove reliable (e.g., Denoise module if its `strength`, `minor_deblur` etc. parameters work via CLI).

