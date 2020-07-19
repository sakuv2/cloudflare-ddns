## CloudFlare DDNS

### Usage

```bash
docker run -d --rm \
    -e EMAIL="login_email@example.com" \
    -e TOKEN="API_TOKEN" \
    -e ZOON="example.com" \
    -e DNS_NAME="host.example.com" \
    cloudflare-ddns
```