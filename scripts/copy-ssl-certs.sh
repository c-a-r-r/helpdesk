#!/bin/bash
# Copy SSL certificates for Docker containers

DOMAIN="helpdesk.amer.biz"
SSL_DIR="./nginx/ssl"

echo "Copying SSL certificates for $DOMAIN..."

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Copy actual certificate files (not symlinks)
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/"
    
    # Set proper ownership
    sudo chown $USER:$USER "$SSL_DIR"/*.pem
    
    # Set proper permissions
    chmod 644 "$SSL_DIR/fullchain.pem"
    chmod 600 "$SSL_DIR/privkey.pem"
    
    echo "SSL certificates copied successfully!"
    echo "Files in $SSL_DIR:"
    ls -la "$SSL_DIR"
else
    echo "Error: SSL certificates not found for $DOMAIN"
    echo "Make sure certbot has generated certificates first"
    exit 1
fi
