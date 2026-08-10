# Project Glossary (CONTEXT.md)

A project may keep a domain glossary at its repo root: `CONTEXT.md`. It maps the project's own words to one agreed meaning so every artifact — questions, specs, task titles, names in code — uses the same language.

**Read:** if `CONTEXT.md` exists at the project root, read it before drafting anything and use its terms verbatim.

**Write:** when the user and you agree on a new term, or sharpen a fuzzy one, append it to `CONTEXT.md` (create the file on the first term). One entry per term:

```markdown
**Term** — plain-words meaning. _Avoid:_ synonyms it replaces.
```

**Conflict:** if the user's wording contradicts an existing glossary entry, ask which wins before proceeding, then record the answer. Never rename an established term silently.
