# SSL Certificate Directory

This directory is intended for storing SSL/TLS certificates for production deployment.

## Required Files

For HTTPS deployment, you need to place the following files in this directory:

- `cert.pem` - Your SSL certificate (including any intermediate certificates)
- `key.pem` - Your private key
- `chain.pem` - Certificate chain (optional, if not included in cert.pem)

## Getting SSL Certificates

### Let's Encrypt (Recommended for Production)

```bash
# Install certbot
sudo apt update
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates to this directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./key.pem
sudo cp /etc/letsencrypt/live/your-domain.com/chain.pem ./chain.pem
```

### Self-Signed Certificate (Development Only)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout key.pem \
    -out cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

## Security Considerations

1. **Private Key Protection**: Ensure `key.pem` has proper permissions:
   ```bash
   chmod 600 key.pem
   ```

2. **Backup**: Keep backups of your certificates and private keys in a secure location.

3. **Renewal**: Set up automatic renewal for Let's Encrypt certificates:
   ```bash
   sudo certbot renew --dry-run
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

4. **Certificate Chain**: Ensure your certificate includes the full chain for proper validation.

## Nginx Configuration

The nginx configuration in `nginx.prod.conf` expects these certificates to be present when using HTTPS.