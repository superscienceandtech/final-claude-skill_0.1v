# Compatibility

This repository is intentionally provider-neutral.

## Status model

Use the following status labels when describing compatibility or verification:

- VERIFIED: confirmed by actual repository evidence
- PARTIALLY VERIFIED: some evidence exists, but not full validation
- UNVERIFIED: no direct evidence available
- NOT SUPPORTED: the platform or workflow is not supported by the current repository evidence

## Canonical skill compatibility

The implementation workflow is designed to be usable across repositories and providers without embedding vendor-specific assumptions. The canonical behavior is the engineering workflow itself, while any provider-specific adapter is considered separate and optional. This design intent is not evidence of compatibility with a specific provider.

## Validator platform support

The repository-audit structural validator requires POSIX directory-descriptor
opens with `O_NOFOLLOW` and fails closed on non-POSIX systems. Canonical
Skill-file validation on Windows is unsupported; the validator returns
`SKILL_PATH_INVALID` before reading the file. The GitHub Actions workflow tests
on Ubuntu with Python 3.12. Windows test-suite runs do not establish Windows
validator support, and symlink-dependent tests may be skipped when the host
does not permit symlink creation.
