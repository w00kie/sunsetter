# Sunsetter

Choose a viewpoint and a sightline on the map to find the two days each year when the sun rises or sets in that direction.

The app runs as one Cloudflare Python Worker. Static assets are served by Workers Assets, the map uses MapLibre with OpenFreeMap tiles, and the astronomy calculation uses only the Python standard library.

## Requirements

- Python 3.14 for local development (Cloudflare currently executes Python Workers on 3.13)
- [uv](https://docs.astral.sh/uv/)
- [Bun](https://bun.sh/) (Node/npm also work with equivalent commands)
- Node 20–24 for pywrangler (Node 26 is not yet supported)

## Develop

```sh
uv sync
bun install
bun run dev
```

Open the local URL printed by pywrangler. No map API key or other environment variables are needed.

## Test

```sh
bun run test
```

## Deploy

Authenticate once with `uv run pywrangler login`, then deploy the Worker and its assets together:

```sh
bun run deploy
```

Python Workers are currently a Cloudflare beta feature. uv selects Python 3.14 locally through `.python-version`; Cloudflare currently selects its Python 3.13/Pyodide runtime from `compatibility_date`. The application code is tested on 3.14 and remains 3.13-compatible until Cloudflare exposes a 3.14 runtime.
