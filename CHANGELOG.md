## [0.1.2] - 2025-11-11

### Added
- Support for Syloti Nagri script (`Sylo`, Unicode block U+A800–U+A82F).
- Tests for Syloti Nagri in range access and script detection.

### Changed
- `clean_script` punctuation configuration now supports levels: `"ascii"`, `"extended"`, and `"all"`.
  - `"ascii"`: ASCII sentence punctuation and quotes only.
  - `"extended"`: ASCII + curly quotes + guillemets + script-specific marks + fullwidth + () [] {} <>.
  - `"all"`: `extended` plus broader general punctuation blocks.
- Backward compatibility: `{"punctuation": True}` maps to `"ascii"`; `False` remains unchanged.

### Fixed
- Preserve ASCII quotes when `symbols=False` and `punctuation=True`.
- Align punctuation handling with levels so script-specific punctuation is only included when using `"extended"` or higher.

## [0.1.1] - 2025-11-01

### Added
- Trusted publishing via GitHub Actions with OIDC (`.github/workflows/publish.yml`).
- Upgraded publish script to a more robust Python implementation (`scripts/publish.py`).
- Increased testing coverage from Python 3.8 to 3.14.

### Fixed
- Export `clean_script` from the public package API.
