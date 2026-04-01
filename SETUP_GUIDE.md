# Setup & First Run Guide

## What's New

✅ **batch_process.py** - Full automation! No more manual copy-paste to Claude chat.
✅ **README.md** - Complete documentation
✅ **jd/** folder - Place your job descriptions here
✅ **responses/** folder - Will store Claude's JSON responses (auto-created)
✅ **.gitignore** updated - Excludes sensitive files

## One-Time Setup

1. **Install dependencies** (if not already done)
   ```bash
   pip install anthropic python-docx lxml docx2pdf
   ```

2. **Get your Anthropic API key**
   - Visit https://console.anthropic.com/
   - Create account / log in
   - Generate API key

3. **Set environment variable**

   **Windows PowerShell:**
   ```powershell
   $env:ANTHROPIC_API_KEY="your-key-here"
   ```

   **Windows CMD:**
   ```cmd
   set ANTHROPIC_API_KEY=your-key-here
   ```

   **Linux/Mac (bash):**
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

   **Permanent:** Add to your shell profile (~/.bashrc, ~/.zshrc, or System Environment Variables)

4. **Verify your template exists**
   ```bash
   python rebuild_cv.py
   ```
   This creates `AamirAli_Resume_ATS.docx` if you haven't already.

## How to Use (Daily)

### Step 1: Collect Job Descriptions

For each job you want to apply to:

1. Copy the full job description text
2. Create a file in the `jd/` folder:
   ```
   jd/Titanbay_Senior_Analytics_Engineer.txt
   jd/Global_Lead_Data_Engineer_MLOps.txt
   jd/Zilch_Senior_Analytics_Engineer.txt
   ```
   Tip: Use `Company_Role.txt` format for clear filenames.

### Step 2: Run Batch Processor

```bash
python batch_process.py
```

That's it! The script will:

1. Read each JD in `jd/`
2. Send to Claude API (Sonnet by default)
3. Save responses to `responses/` folder
4. Generate tailored `.docx` and `.pdf` in `generated_resumes/`
5. Create `batch_summary.md` with ATS scores

### Step 3: Review & Apply

Check the generated resumes:

```bash
# Open the folder
start generated_resumes   # Windows
open generated_resumes    # Mac
xdg-open generated_resumes  # Linux
```

Review each `.docx` file, make any tweaks if needed, then submit!

## Command Options

```bash
# Use cheaper/faster model
python batch_process.py --model claude-haiku-3-5

# Skip JDs that already have responses (for re-runs)
python batch_process.py --skip-existing

# Preview without sending to API
python batch_process.py --dry-run

# Change JD directory
python batch_process.py --jd-dir my_jobs/
```

## Tips

- **Cost:** Haiku costs ~$0.001 per JD, Sonnet ~$0.015. 100 JDs = ~$1-15
- **Quality:** Sonnet gives better results; Haiku is great for bulk screening
- **Rate limits:** Script adds 2-second delays. If you hit limits, add `--model haiku` or add `--delay` flag (future)
- **PDFs:** Need MS Word or LibreOffice installed. If conversion fails, .docx is still generated.
- **API key security:** Never commit your API key. Use environment variable only.

## Troubleshooting

**"ANTHROPIC_API_KEY not set"**
→ Set it as shown in Step 3 above. Verify with `echo %ANTHROPIC_API_KEY%` (CMD) or `echo $env:ANTHROPIC_API_KEY` (PowerShell).

**"Template not found: AamirAli_Resume_ATS.docx"**
→ Run `python rebuild_cv.py` first to create the ATS template.

**PDF not generated**
→ Install [MS Word](https://www.microsoft.com/) or [LibreOffice](https://www.libreoffice.org/)
→ Or manually convert .docx to PDF using Google Docs/online converter

**Low ATS score (<70%)**
→ Consider editing your CV_CONTENT in tailor_resume.py to add more relevant skills
→ Re-run batch with --model claude-sonnet-4-6 for better quality
→ Manually tweak the generated response.json and re-run --mode apply

**"ImportError: No module named anthropic"**
→ `pip install anthropic`

## File Reference

- `tailor_resume.py` - Original 2-step tool (still works)
- `batch_process.py` - **NEW** automated batch processor (use this!)
- `rebuild_cv.py` - One-time ATS conversion
- `jd/` - Place job descriptions here
- `responses/` - Claude JSON responses (saved automatically)
- `generated_resumes/` - Your tailored resumes (docx + pdf)
- `README.md` - Full documentation

## What About My Old Files?

- `prompt.txt` and `response.json` in root are from manual mode - you can delete them
- `jd.txt` was a single JD - you can move it into `jd/` folder or delete
- Existing manual workflow still works if you prefer it

## Next Steps

1. Set your ANTHROPIC_API_KEY
2. Put 1-2 test JDs in `jd/` folder
3. Run: `python batch_process.py --dry-run` to preview
4. Run: `python batch_process.py` to process for real
5. Check `generated_resumes/` and `batch_summary.md`

---

**Questions?** See README.md for more details.
