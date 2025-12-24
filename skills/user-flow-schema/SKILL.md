---
name: User Flow Schema
description: This skill provides the strict output schema for user flow diagrams. Use when creating user journeys, validating flow structure, or generating Mermaid diagrams for Notion.
---

## Purpose

Define consistent user flow structure for Notion integration. Every flow uses Mermaid diagrams with standardized step types.

## Flow Structure

| Section | Required | Validation |
|---------|----------|------------|
| Name | Yes | Clear journey name |
| Description | Yes | One-line summary |
| Steps | Yes | Entry, actions, decisions, exit |
| Error Handling | Yes | Recovery paths for failures |
| Mermaid | Yes | Valid flowchart code |

## Step Types

| Type | Shape | Use When |
|------|-------|----------|
| `entry` | `([text])` | Starting point |
| `action` | `[text]` | User does something |
| `decision` | `{text?}` | Choice point |
| `success` | `[text]` | Happy path end |
| `error` | `[text]` | Failure state |
| `exit` | `([text])` | Flow terminates |

## Validation Rules

1. Every flow MUST have one entry and at least one exit
2. Decisions MUST have labeled branches (`-->|Yes|`, `-->|No|`)
3. Error states MUST have recovery or exit paths
4. Labels MUST be user-focused (what they see/do), not technical
5. Max 15 steps per flow; split larger flows
6. **NO redundant steps** - Merge steps that happen together; if user sees one screen, that's one step

## References

- `references/mermaid-patterns.md` - Diagram templates and syntax
- `references/template.md` - Flow document template

## Examples

- `examples/valid-flow.json` - Complete login flow example
- `examples/invalid-examples.md` - Common mistakes and fixes

## Quick Validation Checklist

Before saving to Notion:
- [ ] Has entry point (rounded box)
- [ ] Has exit point (rounded box)
- [ ] All decisions have labeled branches
- [ ] Error states have recovery paths
- [ ] Labels describe user actions, not API calls
- [ ] Under 15 steps
- [ ] No redundant steps (one screen = one step)
