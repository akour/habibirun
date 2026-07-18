# Habibi, Run! website

Static, no-build Cloudflare Pages site for:

- `https://habibiapps.com/habibirun/`
- `https://habibiapps.com/habibirun/privacy/`

## Cloudflare Pages

- Framework preset: None
- Build command: leave blank
- Build output directory: `/`

This dedicated repository can be deployed on its own Pages hostname. To serve it specifically below the existing `habibiapps.com/habibirun` path without replacing the current Habibi Apps homepage, either copy the `habibirun/` directory into the existing domain's Pages repository or route that path through a Cloudflare Worker to this Pages project.
