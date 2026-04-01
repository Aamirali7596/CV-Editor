# Setup & First Run Guide

## What's New

✅ **tailor_resume.py** - Stable two-step workflow with Claude
✅ **README.md** - Complete documentation
✅ **jd/** folder - Place your job descriptions here (optional)
✅ **.gitignore** updated - Excludes sensitive files

## One-Time Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get your Claude API key**
   - Visit https://console.anthropic.com/ (or https://openrouter.ai/ for OpenRouter)
   - Create account / log in
   - Generate API key

3. **Set API Key** (Choose ONE method)

   **Method A: .env file (Recommended)**
   ```powershell
   # Create .env file in project root with:
   ANTHROPIC_API_KEY=your-key-here
   
   # Or for OpenRouter:
   ANTHROPIC_AUTH_TOKEN=your-openrouter-key
   ANTHROPIC_BASE_URL=https://openrouter.ai/api
   ANTHROPIC_MODEL=anthropic/claude-3-5-haiku:free
   ```

   **Method B: Environment variable**
   ```powershell
   # Windows PowerShell:
   $env:ANTHROPIC_API_KEY="your-key-here"
   
   # Windows CMD:
   set ANTHROPIC_API_KEY=your-key-here
   
   # Linux/Mac:
   export ANTHROPIC_API_KEY="your-key-here"
   ```

   **Method C: Permanent system variable**
   - Press `Win + X` → System → Advanced system settings
   - Click "Environment Variables"
   - Under "User variables" → New
   - Name: `ANTHROPIC_API_KEY`, Value: `your-key`
   - OK → OK → OK
   - **Restart your terminal**

4. **Verify your template exists**
   ```bash
   python rebuild_cv.py
   ```
   This creates `AamirAli_Resume_ATS.docx` if you haven't already.

## How to Use (Daily)

### Step 1: Generate Prompt

For each job you want to apply to:

1. Copy the full job description text (or have it in a file)
2. Run the prep command:
   ```bash
   python tailor_resume.py --mode prep --jd job_description.txt
   ```
   Or manually paste:
   ```bash
   python tailor_resume.py --mode prep
   ```
3. Copy the generated prompt from `prompt.txt`
4. Paste into Claude's chat at https://claude.ai
5. Wait for Claude's response containing the JSON

### Step 2: Apply Tailored Resume

1. Copy Claude's full JSON response
2. Save it as `response.json` in the project root
3. Run:
   ```bash
   python tailor_resume.py --mode apply
   ```
4. Find your tailored resume in `generated_resumes/` as `.docx` and `.pdf`

### Optional: Check ATS Compliance

Verify your generated resume is ATS-friendly:
```bash
python tailor_resume.py --mode check --doc generated_resumes/Your_Company.docx
```

## Tips

- **Quality JDs:** Use the full job description, not just bullet points
- **ATS Score:** The JSON response includes `ats_match_percentage`. Aim for 80%+
- **Review:** Always open the generated .docx and verify formatting before submitting
- **Iterate:** If ATS score is low, consider adding missing keywords to your `CV_CONTENT` permanently and re-run

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
→ Set it as shown in Step 3 above. Verify with `echo %ANTHROPIC_API_KEY%` (CMD) or `echo $env:ANTHROPIC_API_KEY` (PowerShell).

**"Template not found: AamirAli_Resume_ATS.docx"**
→ Run `python rebuild_cv.py` first to create the ATS template.

**PDF not generated**
→ Install [MS Word](https://www.microsoft.com/) or [LibreOffice](https://www.libreoffice.org/)
→ Or manually convert .docx to PDF using Google Docs/online converter
→ The .docx is always generated even if PDF fails

**JSON parse errors**
→ Make sure you're copying Claude's full JSON response (no extra commentary)
→ The script automatically strips markdown fences if Claude adds them
→ If errors persist, check the raw output in `debug_claude_response.txt`

**Rate limits**
→ Anthropic/OpenRouter has rate limits based on your plan
→ If you hit limits, wait a minute and retry or upgrade your plan

**Import errors**
→ `pip install -r requirements.txt` to ensure all dependencies are installed

## File Reference

```
Resume_editor/
├── AamirAli_Resume_ATS.docx      # Your ATS-friendly template (untracked)
├── tailor_resume.py              # Main script (2-step workflow)
├── rebuild_cv.py                 # Rebuild template from original
├── requirements.txt              # Python dependencies
├── jd/                           # Job description files (optional)
│   └── example_job.txt
├── prompt.txt                    # Generated (temporary)
├── response.json                 # Claude's JSON reply (temporary, gitignored)
└── generated_resumes/            # Tailored resumes (created)
    └── Company_Role.docx
```

## Cost Estimate

**Claude pricing (as of 2025):**
- Sonnet 3.5: ~$3 per 1M input tokens, $15 per 1M output
- Haiku 3.5: ~$0.25 per 1M input, $1.25 per 1M output

**Typical cost per JD:**
- Input: ~2k tokens (resume + JD) + Output: ~1k tokens
- Haiku: ~$0.001 per JD
- Sonnet: ~$0.015 per JD

So 100 job applications = ~$1 (Haiku) to ~$15 (Sonnet).

## Next Steps

1. Set your `ANTHROPIC_API_KEY`
2. Run `python rebuild_cv.py` to create template
3. Prepare a job description file or copy one to clipboard
4. Run: `python tailor_resume.py --mode prep --jd your_job.txt`
5. Paste prompt into Claude, save response as `response.json`
6. Run: `python tailor_resume.py --mode apply`
7. Check `generated_resumes/` for your tailored resume

---

**Questions?** See README.md for more details.
