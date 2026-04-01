# Contributing to Resume Tailor

Thank you for your interest in improving this tool! This guide explains how to set up your development environment and contribute while keeping personal data separate.

## Development Setup

### 1. Fork and Clone

```bash
# Fork this repository on GitHub, then:
git clone https://github.com/yourusername/Resume_editor.git
cd Resume_editor
```

### 2. Create Your Personal Dev Branch

**Important:** The repository maintains a clean `main` branch without any personal data. Your personal resume should never be committed to `main`.

```bash
# Checkout main and pull latest
git checkout main
git pull origin main

# Create your personal development branch
# Version starts at v1_001 - increment by 1 for your fork
git checkout -b dev_YourName_v1_002
```

Replace:
- `YourName` with your actual name (e.g., `dev_JohnDoe_v1_002`)
- Version number: if the base is `v1_001`, your fork should be `v1_002`

### 3. Add Your Personal Data (Locally Only)

Create `my_cv_data.py` (this file is gitignored - never commit it!):

```python
# my_cv_data.py - YOUR RESUME (gitignored, do not commit!)

CV_CONTENT = """Your full resume content here..."""

COMPANIES = [
    "Your Current Company",
    "Previous Company 1",
    "Previous Company 2",
    "Previous Company 3",
]
```

### 4. Create Your Template File

Create `YourName_Resume_ATS.docx` (or keep `AamirAli_Resume_ATS.docx` if you prefer) with your ATS-friendly resume formatted with the same structure as described in `tailor_resume.py`.

This file is also gitignored - **never commit your actual resume**.

## Making Changes

### Workflow

1. **Always work on your dev branch** (never main):
   ```bash
   git checkout dev_YourName_v1_002
   ```

2. **Make your changes** to the code (not to personal data files)
   - Improve the prompt logic
   - Add new features
   - Fix bugs
   - Update documentation

3. **Test with your personal data** (using `my_cv_data.py` and your template)

4. **Ensure no personal data leaks**:
   ```bash
   # Check for personal info before committing
   git status
   # Make sure my_cv_data.py and *.docx are not staged
   ```

5. **Commit your code changes only**:
   ```bash
   git add tailor_resume.py README.md  # etc - never add my_cv_data.py
   git commit -m "feat: add new feature description"
   ```

### Code Guidelines

- Keep personal data out of the code (no hardcoded company names, etc.)
- Use `CV_CONTENT` and `COMPANIES` from `my_cv_data.py` (already imported)
- Maintain Python 3.10+ compatibility
- Keep dependencies minimal (see requirements.txt)

### Updating Documentation

When you add features or change workflows, update:
- README.md (user-facing documentation)
- SETUP_GUIDE.md (setup instructions)
- CONTRIBUTING.md (if needed)

## Sharing Your Improvements

### Option 1: Keep as Personal Fork

Your dev branch is your personal workspace. You can use it indefinitely and make it your own.

### Option 2: Submit Pull Request to Base Repo

If you've made generic improvements (non-personal code changes), you can submit a PR:

1. **Ensure no personal data** in your commits:
   ```bash
   git diff main --name-only  # Should NOT show my_cv_data.py or any .docx
   ```

2. **Rebase onto latest main**:
   ```bash
   git checkout dev_YourName_v1_002
   git fetch origin
   git rebase origin/main
   ```

3. **Create a clean branch for PR** (without your personal branch naming):
   ```bash
   git checkout -b feature/your-feature-name
   # Squash commits to remove any accidental personal data references
   # Ensure the branch is clean
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a PR on GitHub targeting `main`.

5. **PR Requirements**:
   - No personal data anywhere in the diff
   - Clear description of changes
   - Updated documentation if needed
   - All tests pass (if any)

## Branch Naming Convention

- `main` - clean, shareable code (no personal data)
- `dev_YourName_v1_XXX` - your personal development branch
- `feature/short-description` - feature branches off your dev branch
- `fix/issue-description` - bug fix branches

### Version Numbering

Increment the version when creating your dev branch:
- Base: `v1_001`
- First fork: `v1_002`
- Next change: `v1_003`
- Major changes: `v2_001`

Format: `vMAJOR_MINOR` (three digits each)

## Notes on Personal Data

**What is considered personal data?**
- Your resume content (companies, dates, achievements)
- Your name in filenames (`AamirAli_Resume_ATS.docx`)
- `my_cv_data.py` (contains your CV)
- Any JD files you add to `jd/` (they're gitignored)

**Why is it gitignored?**
This repository is designed to be a tool, not a storage for your private information. Keeping personal data out of version control:
- Protects your privacy
- Makes the repo shareable as a template
- Reduces risk of accidental exposure

**What IS safe to commit?**
- Code changes (`tailor_resume.py`, `rebuild_cv.py`)
- Documentation updates (README, SETUP_GUIDE)
- Generic configuration (no personal values)
- Scripts and utilities

## Questions?

Open an issue on GitHub for bugs, feature requests, or questions about contributing.

---

**Happy coding!** 🚀
