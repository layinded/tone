# Changelog

All notable changes to the TONE project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Changed
- Project renamed from **TOON** to **TONE** (Token-Optimized Notation Engine)
- Version bumped from 0.5.1 to 1.0.0
- Author updated to Abdulbasit Ayinde
- Description updated to emphasize LLM optimization

### Fixed
- **Critical**: Fixed import errors when optional dependencies (FastAPI, Pydantic, Pandas) are not installed
- FastAPI integration now safely handles missing dependencies
- Pydantic integration properly handles `TypeVar` when BaseModel is unavailable
- All integration modules now use conditional imports

### Added
- Support for both `.tone` and `.toon` file extensions for backwards compatibility
- Comprehensive test suite in `tone-test/` directory
- Token comparison utilities with detailed savings reporting

### Documentation
- Consolidated all documentation into single `README.md`
- Updated all examples and references from TOON to TONE
- Added comprehensive testing instructions

### Technical
- Proper handling of optional dependencies across all integration modules
- Improved error messages for missing dependencies
- Linter-clean code across entire codebase

## [0.5.1] - Original TOON Package

Initial Python port of TOON from TypeScript reference implementation.

