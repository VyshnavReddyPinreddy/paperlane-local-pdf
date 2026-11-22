# Paperlane — Local PDF Workspace

A clean, private PDF website that runs **entirely on your computer** through `http://127.0.0.1:8765`. Includes 19 PDF tools from the provided reference, excluding the crossed-out tools. No accounts, external API, telemetry, trial limits, file-count restrictions, or cloud uploads.

## Quick start on Windows

1. Extract this ZIP to a permanent folder. **Do not run it inside the ZIP.**
2. Install [Python 3.10 or newer](https://www.python.org/downloads/) if you do not already have it. During installation, enable **Add Python to PATH**.
3. Double-click **`START_WINDOWS.bat`**. The first launch creates a `.venv` folder and installs Python packages. Internet access is needed **only to download those packages on initial setup**.
4. Your browser opens at `http://127.0.0.1:8765`.
5. To close the application, close the command prompt window or press **Ctrl+C** in it.

The start script does not install LibreOffice. For Word, PowerPoint, Excel and HTML conversion, install the **offline LibreOffice desktop app** from [libreoffice.org](https://www.libreoffice.org/), then restart Paperlane. If you already have it, Paperlane normally finds it automatically. You can set the `LIBREOFFICE_PATH` environment variable to the full path to `soffice.exe` if auto-detection fails.

## Mac and Linux

Run `./START_MAC_LINUX.sh` in Terminal (or `bash START_MAC_LINUX.sh`). This creates a local Python virtual environment on first launch, then opens Paperlane. Install LibreOffice separately for Office/HTML conversions.

If Python venv support is missing on Ubuntu, install `python3-venv` through your package manager. If your browser does not open automatically, browse to `http://127.0.0.1:8765` yourself.

## The included tools

| Group | Tools |
| --- | --- |
| Organize PDF | Merge PDF, Split PDF, Remove pages, Extract pages, Organize PDF, Scan to PDF |
| Optimize PDF | Compress PDF |
| Convert to PDF | JPG to PDF, Word to PDF, PowerPoint to PDF, Excel to PDF, HTML to PDF |
| Convert from PDF | PDF to JPG |
| Edit PDF | Rotate PDF, Add page numbers, Add watermark, Crop PDF |
| PDF Security | Unlock PDF, Protect PDF |

**Batch processing:** All single-PDF tools except the visual page organizer can process multiple files together. Multiple outputs are downloaded in one ZIP. Drag files into the workspace or use Add folder. PDFs of many pages are supported; the organizer loads thumbnails incrementally, rather than rendering everything at once. The organizer's "Load all pages" action is available for large PDFs.

### Important accuracy/format notes

- **Compress PDF:** Lossless mode rearranges/compresses PDF structures; balanced/strong additionally downsample and recompress compatible embedded photographic images. Text and vector objects remain searchable and selectable. Sometimes output cannot be made smaller; compression is not a guarantee.
- **Scan to PDF:** Combines images/camera photos into PDF. Does **not** communicate directly with a USB flatbed scanner or perform OCR.
- **Convert Word/PowerPoint/Excel:** Uses local LibreOffice headless conversion. Complicated MS Office layouts, unusual fonts, and complex spreadsheets may differ from Microsoft Office's own PDF exporter.
- **HTML to PDF:** Uses LibreOffice's HTML import, not a full browser rendering engine. Scripts/iframes and common external resource references are stripped to reduce exposure to external resources, and some advanced CSS may not reproduce accurately. For trusted HTML only.
- **Crop PDF:** Adjusts the visible crop box. It does **not securely redact** content outside the crop area.
- **Unlock PDF:** Requires the correct document password. This is **not** a password-cracking tool.
- **Protect PDF:** Uses AES-256 encryption. Use separate opening and owner passwords for meaningful permission restrictions. PDF permissions depend on the viewer respecting them; encryption is the important confidentiality control.
- **Watermarks/page numbers:** These overlay the existing pages. Existing digital signatures may be invalidated by modifications.

## Privacy and local processing

- The webserver binds **only to `127.0.0.1`** (loopback), not to your network interface or the Internet.
- No cloud endpoints, advertisements, telemetry, cookies, CDN fonts, or analytics appear in the source code.
- PDFs/documents and outputs are handled through a per-job folder in your **operating system's temporary directory**, using the local Python process. Preview uploads are deleted after rendering. Finished outputs remain in the temporary directory for up to **one hour** to allow re-downloading, and are removed when the server exits normally. A forced crash may leave temporary files until the OS clears them. For extremely sensitive documents, you may manually clear your OS temp folder once finished.
- The **first installation** downloads Python packages from PyPI when you run the startup script. Installing LibreOffice may also require downloading its installer. After setup, the PDF operations themselves need no network connection.
- No artificial quotas exist for files, pages, job count or daily operations. Actual processing is limited by your system's memory, disk space, and performance. Particularly large image/PDF conversions can take significant CPU and disk resources.

## Command line / development

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python app.py --no-browser
```

Use `python app.py --port 8888` if the default port is busy. No `.env`, keys, database, or Node installation is needed.

### Files

```
Paperlane_Local_PDF/
├── app.py                 # localhost-only FastAPI HTTP application
├── engine.py              # PDF, image and office converters
├── static/
│   ├── index.html         # website
│   ├── style.css          # responsive design
│   ├── app.js             # tools, previews and download behavior
│   └── favicon.svg
├── requirements.txt       # local Python dependencies
├── START_WINDOWS.bat
├── START_MAC_LINUX.sh
├── tests/
│   └── test_engine.py
└── README.md
```

## Troubleshooting

**The browser says site cannot be reached** — Keep the command prompt open. Check startup errors. Only browse to `127.0.0.1:8765`, not some online address.

**Python not found** — Install Python 3.10+ and check Add Python to PATH. Restart your terminal.

**LibreOffice not detected** — Install LibreOffice desktop, close and reopen Paperlane. Alternatively supply `LIBREOFFICE_PATH` as the `soffice.exe` location.

**Windows Defender/SmartScreen displays a warning** — The ZIP contains readable Python and JavaScript source code, not a signed `.exe`. You can inspect the files yourself before running. Do not disable your antivirus.

**PDF has a password** — Enter the known password in Tool settings. For files with different passwords, process them separately.

**Output isn't smaller / lossless compression grows** — Compression depends on the images, fonts and object structure of the original document; files may be minimally compressible.

**Browser tab closed** — Keep the command prompt open and visit `http://127.0.0.1:8765` again. The browser is the interface, the Python process is the engine.

## Release notes (v1.0)

This first version is a fully local web application, **not yet a bundled native Windows `.exe`**. A native desktop package can be built after you test the tool behavior and UI. No changes are needed to your sensitive documents or the network settings for normal use.