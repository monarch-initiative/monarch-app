# Link Previews (Dynamic Open Graph Meta Tags)

## Overview

When sharing Monarch Initiative entity links on social media platforms (Slack, Twitter, Discord, Mastodon, Bluesky, etc.), the platform displays a "link preview" with the page title, description, and image. These previews are generated from Open Graph (OG) meta tags in the HTML.

Since Monarch is a Single Page Application (SPA), the initial HTML served by nginx contains generic site-wide meta tags. Social media crawlers don't execute JavaScript, so they can't see the dynamic, entity-specific content.

## Solution

We detect social media crawler requests at the nginx level and route them to a special `/meta` endpoint that serves HTML with entity-specific OG tags.

### Architecture

```
Request for /MONDO:0005148
         │
         ▼
      Nginx
         │
         ├─── Is User-Agent a bot? ───► Yes ──► Proxy to /v3/api/meta/MONDO:0005148
         │                                              │
         │                                              ▼
         │                                      FastAPI fetches entity from Solr,
         │                                      returns HTML with dynamic OG tags
         │
         └─── No (regular user) ──► Serve index.html (SPA loads normally)
```

### Supported Crawlers

The following User-Agents are detected and served dynamic meta tags:

- Slackbot
- Twitterbot
- facebookexternalhit
- LinkedInBot
- Discordbot
- WhatsApp
- TelegramBot
- Mastodon
- Bluesky
- Googlebot
- bingbot
- Embedly
- Pinterest
- Applebot
- Quora Link Preview
- Outbrain

### Entity Path Detection

Only paths matching the CURIE format are eligible for dynamic meta tags:
- `/MONDO:0005148` ✓
- `/HP:0001234` ✓
- `/HGNC:1234` ✓
- `/about` ✗ (not a CURIE)
- `/results` ✗ (not a CURIE)

### Dynamic URL Support

The meta endpoint derives URLs from the request headers, so the same deployment works for both:
- `beta.monarchinitiative.org` → OG tags reference beta URLs
- `monarchinitiative.org` → OG tags reference production URLs

No configuration changes needed between environments.

## Testing

### Manual Testing

Test as a regular browser (should get the SPA):
```bash
curl -s http://localhost:8080/MONDO:0005148 | head -20
```

Test as Slackbot (should get entity-specific OG tags):
```bash
curl -s -H "User-Agent: Slackbot" http://localhost:8080/MONDO:0005148 | grep og:
```

Test as Mastodon (should get entity-specific OG tags):
```bash
curl -s -H "User-Agent: Mastodon/4.0" http://localhost:8080/MONDO:0005148 | grep og:
```

Test as Bluesky (should get entity-specific OG tags):
```bash
curl -s -H "User-Agent: Bluesky" http://localhost:8080/MONDO:0005148 | grep og:
```

### Automated Testing

Run the nginx bot detection tests:
```bash
NGINX_URL=http://localhost:8080 ./services/nginx/tests/test_bot_detection.sh
```

Run the backend unit tests:
```bash
cd backend && uv run pytest tests/api/test_meta.py -v
```

## Configuration

### Customizing Detected Bots

Edit `services/nginx/config/default.conf` to add or remove User-Agent patterns from the `$is_bot` map.

### Files

| File | Purpose |
|------|---------|
| `backend/src/monarch_py/api/meta.py` | FastAPI endpoint that renders OG tags |
| `backend/src/monarch_py/api/templates/meta.html` | Jinja2 template for HTML response |
| `services/nginx/config/default.conf` | Nginx bot detection and routing |
| `services/nginx/tests/test_bot_detection.sh` | Integration test script |
