# Automatic enforcement (Claude Code only)

The skill's own workflow tells the agent to run `scripts/detect.py` on the files it
touched before finishing. That works in any agent with shell access, but it is still an
instruction — a smaller model sometimes skips it, which is exactly where the residual
defects in our benchmark came from.

A **hook** removes the choice: Claude Code runs it after every file write, and the
findings come back to the agent as feedback it has to deal with. Nothing else in this
skill depends on Claude Code, so this file is opt-in.

## Setup

Add to `.claude/settings.json` in your project (create the file if it does not exist):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/skills/rtl-design/scripts/detect.py \"$CLAUDE_FILE_PATHS\" --format text || true"
          }
        ]
      }
    ]
  }
}
```

- `matcher` limits it to file-writing tools, so reads and searches stay fast.
- `|| true` keeps a finding from failing the tool call — the agent sees the report and
  fixes it, rather than the write being rejected.
- If you installed globally (`npx skills add … -g`), point the path at
  `~/.claude/skills/rtl-design/scripts/detect.py` instead.

Drop `|| true` if you would rather the write be blocked outright until the file is clean.
That is stricter than most projects want, but it is the strongest available guarantee.

## Scope it if the repo is mixed

For a repo that is only partly Persian, narrow the matcher or point the command at the
directory that holds the localized UI, so the hook stays quiet elsewhere:

```json
"command": "python3 .claude/skills/rtl-design/scripts/detect.py src/locales src/components/fa --format text || true"
```

## Other agents

Cursor, Codex CLI and Gemini CLI have no equivalent post-write hook today. There, the
workflow step in `SKILL.md` is the mechanism — and a CI job is the backstop:

```yaml
- run: python3 skills/rtl-design/scripts/detect.py ./src
```

Exit code 1 on any finding, so a pull request that reintroduces a defect fails the build.
