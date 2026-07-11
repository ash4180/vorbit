# Vorbit Mock Registry Contract

Use the runtime resolver's `storage_root` and `project_slug`. The primary path is `<storage-root>/projects/<project-slug>/mock-registry.json`; only use project-local `.vorbit/mock-registry.json` as an explicitly reported legacy fallback.

The file uses schema 1.1:

```json
{
  "version": "1.1",
  "mocks": [
    {
      "feature": "saved-searches",
      "type": "file",
      "path": "src/features/saved-searches/mocks/data.json",
      "endpoint": "proposed:GET /api/saved-searches",
      "createdBy": "prototype",
      "createdAt": "2026-01-01T00:00:00Z",
      "components": ["src/features/saved-searches/data-source.ts"]
    }
  ]
}
```

Each `mocks` item records one application integration boundary:

- `feature`: stable feature name;
- `type`: `file` or `state`;
- `path`: project-relative source path;
- `endpoint`: confirmed method/path, or `proposed:<method path>` until backend approval;
- `createdBy`: `prototype` or `implement`;
- `createdAt`: ISO 8601 timestamp;
- `components`: production consumers of the boundary;
- `location` and `stateType`: required only for a `state` item.

Never register test fixtures, stories, examples, seeds, or static demo data. Validate an existing root/version before editing, avoid duplicate feature/path entries, and write updates atomically. Remove an entry only after the real integration passes and the mock has no production consumers.
