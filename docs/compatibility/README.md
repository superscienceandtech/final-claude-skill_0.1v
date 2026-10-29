# Compatibility

This repository is intentionally provider-neutral.

## Status model

Use the following status labels when describing compatibility or verification:

- VERIFIED: confirmed by actual repository evidence
- PARTIALLY VERIFIED: some evidence exists, but not full validation
- UNVERIFIED: no direct evidence available
- NOT SUPPORTED: the platform or workflow is not supported by the current repository evidence

## Canonical skill compatibility

The implementation skill is designed to be usable across repositories and providers without embedding vendor-specific assumptions. The canonical behavior is the engineering workflow itself, while any provider-specific adapter is considered separate and optional.
