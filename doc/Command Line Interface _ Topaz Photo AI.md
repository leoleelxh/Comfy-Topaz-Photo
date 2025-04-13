To use the Topaz Photo AI command line interface (CLI), follow the below instructions for your operating system.

Windows:

1.  Open Command Prompt or Terminal
2.  Type in:  
    cd "C:\\Program Files\\Topaz Labs LLC\\Topaz Photo AI"
3.  Type in:  
    .\\tpai.exe --help
4.  Type in:  
    .\\tpai.exe "folder/or/file/path/here"

![](https://cdn.sanity.io/images/r2plryeu/production/45fd256fb694c2ff306b5a16b987852a828d10cd-1787x919.png?q=90&fit=max&auto=format)

* * *

Processing Controls
-------------------

The CLI will use your Autopilot settings to process images. Open Topaz Photo AI and go to the Preferences > Autopilot menu.

Instructions on using the Preferences > Autopilot menu are [here](https://docs.topazlabs.com/photo-ai/enhancements/autopilot-and-configuration).

### Command Options

\--output, -o: Output folder to save images to. If it doesn't exist the program will attempt to create it.

\--overwrite: Allow overwriting of files. THIS IS DESTRUCTIVE.

\--recursive, -r: If given a folder path, it will recurse into subdirectories instead of just grabbing top level files.  
Note: If output folder is specified, the input folder's structure will be recreated within the output as necessary.  

### File Format Options:

\--format, -f: Set the output format. Accepts jpg, jpeg, png, tif, tiff, dng, or preserve. Default: preserve  
Note: Preserve will attempt to preserve the exact input extension, but RAW files will still be converted to DNG.Format Specific Options:

\--quality, -q: JPEG quality for output. Must be between 0 and 100. Default: 95

\--compression, -c: PNG compression amount. Must be between 0 and 10. Default: 2

\--bit-depth, -d: TIFF bit depth. Must be either 8 or 16. Default: 16

\--tiff-compression: -tc: TIFF compression format. Must be "none", "lzw", or "zip".  
Note: lzw is not allowed on 16-bit output and will be converted to zip.  

### Debug Options:

\--showSettings: Shows the Autopilot settings for images before they are processed

\--skipProcessing: Skips processing the image (e.g., if you just want to know the settings)

\--verbose, -v: Print more log entries to console.

Return values:  
0 - Success  
1 - Partial Success (e.g., some files failed)  
\-1 (255) - No valid files passed.  
\-2 (254) - Invalid log token. Open the app normally to login.  
\-3 (253) - An invalid argument was found.