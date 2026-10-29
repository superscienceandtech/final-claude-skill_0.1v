# Providers

This repository intentionally keeps provider-specific logic separate from the canonical implementation skill.

The canonical workflow is provider-neutral; any provider-specific adapter can be added in a dedicated provider integration when repository evidence supports it.

## Claude Code

Claude Code integration uses the documented plugin layout without moving or
copying canonical Skills. The repository root contains
`.claude-plugin/plugin.json`; the plugin's default `skills/` component
directory is the existing canonical Skill directory. The repository's own
registry continues to discover the same files.

The [official plugin component
guide](https://code.claude.com/docs/en/plugins/components#skills) documents
Skills under a plugin's `skills/` directory and namespaced commands. The
[plugin creation guide](https://code.claude.com/docs/en/plugins/create)
documents loading a local plugin with `--plugin-dir`. For a local session, run
`claude --plugin-dir .` from the repository root; the documented command for
the implementation Skill is `/claude-skills-library:implementation`. This is
a local development/loading path, not a marketplace or permanent installation
setup. Runtime discovery must be verified in Claude Code; a valid plugin
layout and passing repository tests alone do not prove that the runtime loaded
it.

### Integration boundary and evidence

- **Data source:** The plugin packages the existing repository-local
  `skills/` directory; it does not create provider-specific copies. The
  repository's native registry independently checks the same Skill sources.
- **Authorization:** A manifest or successful discovery does not authorize
  Skill execution. Execution and tool permissions are governed by the host
  runtime and the task-specific Owner authorization; this repository manifest
  does not enforce a sandbox or least-privilege process boundary.
- **Credentials and external access:** This plugin configuration declares no
  credentials, external service connection, or remote data flow. No external
  integration is implemented by this manifest.
- **Retention and logging:** The manifest defines no data-retention or
  provider logging policy. These behaviors depend on the host runtime and
  remain unverified here.
- **Failure and revocation:** Local plugin loading/invocation failures,
  permission revocation, and recovery behavior have not been exercised in
  this environment. No claim is made about their runtime behavior.
- **Repository evidence:** `tests/test_skill_registry.py` checks the manifest
  metadata and consistency between native Skill discovery and the canonical
  `skills/<name>/SKILL.md` paths. This is a local configuration test, not a
  Claude Code runtime test.

The `claude` executable was not available on PATH in the inspected
environment. Runtime loading and invocation are therefore **NOT VERIFIED**.
Making a Skill discoverable does not authorize its execution. In particular,
the `repository-audit` Skill and its structural validator remain subject to
their separate governance requirements.
