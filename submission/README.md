# submission/ — the only mutable directory

Your PR may change files here and nowhere else (Gate 2 enforces this against
`main:manifest.json`). `manifest.json` declares your artifact; `weights.json`
is the artifact itself (dev mode: in-repo; production: Hippius object, with
`weights_file` replaced by `hippius_object_key` + an encrypted blob).
