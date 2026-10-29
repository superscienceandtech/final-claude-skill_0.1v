# Topic-Specific Recommendations

Use these specific recommendations when a topic is a gap. Paths are relative to this reference file (`.claude/skills/self-assessment/references/`).

**Slash Commands (score 0)**:
- Tutorial: [01-slash-commands/](../../../../01-slash-commands/)
- Focus on: Built-in commands reference, creating your first SKILL.md, `$ARGUMENTS` syntax
- Key exercise: Create a `/optimize` command and test it
- Done when: You can create a custom skill with arguments and dynamic context

**Slash Commands (score 1 — review)**:
- Focus on: Dynamic context with `!`backtick`` syntax, `@file` references, `disable-model-invocation` vs `user-invocable` control
- Done when: You can create a skill that injects live command output and controls its own invocation behavior

**Memory (score 0)**:
- Tutorial: [02-memory/](../../../../02-memory/)
- Focus on: CLAUDE.md creation, `/init` and `/memory` commands, `#` prefix for quick updates
- Key exercise: Create a project CLAUDE.md with your coding standards
- Done when: Claude remembers your preferences across sessions

**Memory (score 1 — review)**:
- Focus on: 7-level hierarchy and priority order, .claude/rules/ directory with path-specific rules, `@import` syntax (max depth 5), Auto Memory MEMORY.md (200-line limit)
- Done when: You have modular rules for different directories and understand the full hierarchy

**Skills (score 0)**:
- Tutorial: [03-skills/](../../../../03-skills/)
- Focus on: SKILL.md format, auto-invocation via description field, progressive disclosure (3 loading levels)
- Key exercise: Install the code-review skill and verify it auto-triggers
- Done when: A skill automatically activates based on conversation context

**Skills (score 1 — review)**:
- Focus on: `context: fork` with `agent` field for subagent execution, `disable-model-invocation` vs `user-invocable`, 2% context budget, bundled resources (scripts/, references/, assets/)
- Done when: You can create a skill that runs in a subagent with forked context

**Hooks (score 0)**:
- Tutorial: [06-hooks/](../../../../06-hooks/)
- Focus on: Configuration structure (matcher + hooks array), PreToolUse/PostToolUse events, exit codes (0=success, 2=block), JSON input/output format
- Key exercise: Create a PreToolUse hook that validates Bash commands
- Done when: A hook blocks dangerous commands before execution

**Hooks (score 1 — review)**:
- Focus on: All 25 hook events (including PostToolUseFailure, StopFailure, TaskCreated, CwdChanged, FileChanged, PostCompact, Elicitation, ElicitationResult), 4 hook types (command, http, prompt, agent), component-scoped hooks in SKILL.md frontmatter, HTTP hooks with allowedEnvVars, `CLAUDE_ENV_FILE` for SessionStart/CwdChanged/FileChanged
- Done when: You can create a prompt-based Stop hook and a component-scoped hook in a skill

**MCP (score 0)**:
- Tutorial: [05-mcp/](../../../../05-mcp/)
- Focus on: `claude mcp add` command, transport types (HTTP recommended), GitHub MCP setup, environment variable expansion
- Key exercise: Add GitHub MCP server and query PRs
- Done when: You can query live data from an external service via MCP

**MCP (score 1 — review)**:
- Focus on: Project-scope .mcp.json (requires team approval), OAuth 2.0 auth, MCP resources with `@server:resource` mentions, Tool Search (ENABLE_TOOL_SEARCH), `claude mcp serve`, output limits (10k/25k/50k)
- Done when: You have a project .mcp.json and understand Tool Search auto mode

**Subagents (score 0)**:
- Tutorial: [04-subagents/](../../../../04-subagents/)
- Focus on: Agent file format (.claude/agents/*.md), built-in agents (general-purpose, Plan, Explore), tools/model/permissionMode config
- Key exercise: Create a code-reviewer subagent and test delegation
- Done when: Claude delegates code review to your custom agent

**Subagents (score 1 — review)**:
- Focus on: Worktree isolation (`isolation: worktree`), persistent agent memory (`memory` field with scopes), background agents (Ctrl+B/Ctrl+F), agent allowlists with `Task(agent_name)`, agent teams (`--teammate-mode`)
- Done when: You have a subagent with persistent memory running in worktree isolation

**Checkpoints (score 0)**:
- Tutorial: [08-checkpoints/](../../../../08-checkpoints/)
- Focus on: Esc+Esc and /rewind access, 5 rewind options (restore code+conversation, restore conversation, restore code, summarize, cancel), limitations (bash filesystem ops not tracked)
- Key exercise: Make experimental changes, then rewind to restore
- Done when: You can confidently experiment knowing you can rewind

**Advanced Features (score 0)**:
- Tutorial: [09-advanced-features/](../../../../09-advanced-features/)
- Focus on: Planning mode (/plan or Shift+Tab), permission modes (5 types), extended thinking (Alt+T toggle)
- Key exercise: Use planning mode to design a feature, then implement it
- Done when: You can switch between planning and implementation modes fluently

**Advanced Features (score 1 — review)**:
- Focus on: Remote control (`claude remote-control`), web sessions (`claude --remote`), desktop handoff (`/desktop`), worktrees (`claude -w`), task lists (Ctrl+T), managed settings for enterprise
- Done when: You can hand off sessions between CLI, web, and desktop

**Plugins (score 0)**:
- Tutorial: [07-plugins/](../../../../07-plugins/)
- Focus on: Plugin structure (.claude-plugin/plugin.json), what plugins bundle (commands, agents, MCP, hooks, settings), installation from marketplace
- Key exercise: Install a plugin and explore its components
- Done when: You understand when to use a plugin vs standalone components

**Plugins (score 1 — review)**:
- Focus on: Creating plugin.json manifest, plugin hooks (hooks/hooks.json), LSP configuration (.lsp.json), `${CLAUDE_PLUGIN_ROOT}` variable, --plugin-dir for testing, marketplace publishing
- Done when: You can create and test a plugin for your team

**CLI (score 0)**:
- Tutorial: [10-cli/](../../../../10-cli/)
- Focus on: Interactive vs print mode, `claude -p` with piping, `--output-format json`, session management (-c/-r)
- Key exercise: Pipe a file to `claude -p` and get JSON output
- Done when: You can use Claude non-interactively in a script

**CLI (score 1 — review)**:
- Focus on: --agents flag with JSON config, --json-schema for structured output, --fallback-model, --from-pr, --strict-mcp-config, batch processing with for loops, `claude mcp serve`
- Done when: You have a CI/CD script that uses Claude with structured JSON output
