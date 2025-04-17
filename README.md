# ISP Throttling Detector

A simple Python script to test whether your ISP is throttling YouTube traffic compared to other sites. It also compares performance with and without a VPN.

## Features

- Measures download speed from:
  - YouTube
  - Google
  - Cloudflare
  - OVH CDN
- Logs all results with timestamps to `log.csv`
- Compares speed before and after VPN activation

## Requirements

- Python 3.7+
- `requests`
- `yt-dlp`
- `rich`

Install dependencies with:

```bash
pip install requests yt-dlp
pip install rich
```
