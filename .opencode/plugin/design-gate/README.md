# Design Gate Bootstrap

The guard loads fail-closed on a clean checkout, but no Design run is accepted
until the native writer and deployment manifest have been built:

```bash
npm --prefix .opencode ci
npm --prefix .opencode run build
```

Start a fresh OpenCode process after every build. The build identity is generated
before compilation and is process-bound; an already-running process must never
adopt newly generated `dist/` bytes.
