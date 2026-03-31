# Changelog

All notable changes to git-summarize will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-03-30

### Added
- **Gemini Provider** - Google Gemini AI support with free tier (60 requests/minute)
  - New `GeminiProvider` class in `providers/gemini.py`
  - Support for `gemini-1.5-flash` and `gemini-1.5-pro` models
  - Free API key from https://aistudio.google.com/app/apikey
  
- **Automated Push Workflow**
  - New `--push` flag for full automation (add → commit → push)
  - Interactive branch selection UI
  - Support for creating new branches during push
  - Push confirmation prompt
  
- **New CLI Flags**
  - `--push` - Enable push after commit with branch selection
  - `--no-add` - Skip `git add .` (use already staged files)
  
- **Configuration Options**
  - `GCM_GEMINI_API_KEY` - Gemini API key (or use `GEMINI_API_KEY`)
  - `GCM_PUSH` - Auto-push setting in config/.env
  - Support for both prefixed (`GCM_*`) and plain environment variables

- **New Modules**
  - `git_summarize/git_ops.py` - Git operations (stage, commit, push, branch management)
  - `git_summarize/providers/gemini.py` - Google Gemini AI provider

### Changed
- Updated default provider in examples to `gemini` (free tier)
- Improved `.env` file loading from package directory
- Enhanced error messages for Git operations
- Updated architecture diagram to include Git Operations module

### Documentation
- Added comprehensive usage examples for `--push` workflow
- Updated configuration section with `.env` file examples
- Added "What's Next?" section with roadmap
- Documented known limitations

### Technical Details
- **Files Added:** 2
  - `src/git_summarize/git_ops.py`
  - `src/git_summarize/providers/gemini.py`
  
- **Files Modified:** 5
  - `src/git_summarize/cli.py` - Push workflow, branch selector
  - `src/git_summarize/ui.py` - Branch selection UI
  - `src/git_summarize/config.py` - Gemini settings, push config
  - `src/git_summarize/providers/__init__.py` - Gemini export
  - `pyproject.toml` - Added `google-generativeai` dependency

---

## [1.0.0] - 2026-03-21

### Added
- Initial release
- Support for Claude, OpenAI, and Ollama providers
- Interactive CLI with Rich UI
- Conventional commit message generation
- Multi-suggestion selection
- Edit/regenerate workflow
- Configuration via environment variables and config file

---

## Future Roadmap

### v1.2.0 (Planned)
- [ ] Pre-commit hook integration
- [ ] Interactive file staging
- [ ] Recent commits history view

### v1.3.0 (Planned)
- [ ] Custom prompt templates
- [ ] Retry logic for API failures
- [ ] Offline mode with prompt caching

### v2.0.0 (Future)
- [ ] Plugin system for third-party providers
- [ ] GitHub/GitLab PR description generation
- [ ] GPG commit signing support

---

## Version History Summary

| Version | Release Date | Key Features |
|---------|-------------|--------------|
| 1.1.0 | 2026-03-30 | Gemini, Auto-push, Branch selector |
| 1.0.0 | 2026-03-21 | Initial release |
