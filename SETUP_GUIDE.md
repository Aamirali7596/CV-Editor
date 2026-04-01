# Setup & First Run Guide

## One-Time Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare your resume template**
   ```bash
   python rebuild_cv.py
   ```
   This creates `AamirAli_Resume_ATS.docx` - your ATS-friendly resume template.

## How to Use

### For each job application:

1. **Generate the prompt**
   ```bash
   python tailor_resume.py --mode prep --jd job_description.txt
   ```
   Or paste the JD interactively:
   ```bash
   python tailor_resume.py --mode prep
   ```

2. **Get Claude's tailored response**
   - Open https://claude.ai in your browser
   - Copy contents of `prompt.txt`
   - Paste into Claude and send
   - Copy Claude's complete JSON reply

3. **Apply the response**
   - Save Claude's JSON as `response.json` in this folder
   - Run:
     ```bash
     python tailor_resume.py --mode apply
     ```
   - Find your tailored resume in `generated_resumes/`

4. **Review**
   - Open the generated `.docx` and verify formatting
   - Check ATS compliance (optional):
     ```bash
     python tailor_resume.py --mode check --doc generated_resumes/Your_Company.docx
     ```

## Tips

- Use the full job description text for best results
- The JSON response includes an ATS match percentage - aim for 80%+
- If score is low, add missing keywords to your `CV_CONTENT` in `tailor_resume.py` and re-run
- Always review the final resume before submitting

## Troubleshooting

**"Template not found: AamirAli_Resume_ATS.docx"**
→ Run `python rebuild_cv.py` to create it.

**PDF not generated**
→ Install MS Word or LibreOffice, or convert manually using online tools.
The `.docx` file is always created even if PDF fails.

**JSON parse error**
→ Ensure you copied Claude's full JSON response (no extra commentary before/after).
The script automatically handles markdown code fences.

## File Structure

```
Resume_editor/
├── AamirAli_Resume_ATS.docx      # Your resume template
├── tailor_resume.py              # Main script
├── rebuild_cv.py                 # Template builder
├── requirements.txt              # Dependencies
├── prompt.txt                    # Generated (temporary)
├── response.json                 # Claude's reply (temporary, gitignored)
├── jd/                           # Optional: store job descriptions
└── generated_resumes/            # Output folder (created)
```

## Notes

- No API key required - uses Claude's web interface
- All processing happens locally on your machine
- Your resume content stays private (only JD is sent to Claude)
- The `generated_resumes/` folder can be gitignored - it contains tailored versions
