# Todo — ai_video_agent

## Planned Features

- [ ] **Thumbnail generator** — 5th sub-agent that feeds `thumbnail_concept` (already in script JSON) to DALL-E 3 and exports a ready-to-upload `thumbnail.png` alongside the MP4.

- [ ] **YouTube upload agent** — 6th sub-agent using YouTube Data API v3 to upload the MP4, set title (`viral_titles[0]`), description, tags, and thumbnail automatically.

- [ ] **`--dry-run` / script preview mode** — CLI flag that stops after `ScriptWriterAgent`, prints the 3 viral titles + scene breakdown, and skips TTS + DALL-E to allow fast prompt iteration without API cost.

- [ ] **Retry & resilience** — Exponential back-off on DALL-E and TTS API calls so a transient rate-limit error doesn't abort the whole run mid-way.

- [ ] **Test suite** — At minimum: unit tests for `ScriptWriterAgent._validate()`, `NewsFetcherAgent` feed parsing, and the JSON schema round-trip.
