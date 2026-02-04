
import os
import sys
import logging
import signal
import argparse
import subprocess
import time
import threading
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("ShareAccess")

def run_ngrok(port):
    try:
        from pyngrok import ngrok, conf
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Check for authentication
        config = conf.get_default()
        if not config.auth_token:
            env_token = os.getenv("NGROK_AUTH_TOKEN")
            if env_token:
                ngrok.set_auth_token(env_token)
                logger.info("Using auth token from environment.")
            else:
                logger.warning("No ngrok auth token found.")
                print("\nTo keep the tunnel alive for more than 2 hours, you need an auth token.")
                print("Get one for free at: https://dashboard.ngrok.com/get-started/your-authtoken")
                token = input("\nEnter your auth token (or press Enter to skip): ").strip()
                if token:
                    ngrok.set_auth_token(token)

        logger.info(f"Opening ngrok tunnel to localhost:{port}...")
        public_url = ngrok.connect(port, bind_tls=True).public_url
        return public_url, "Ngrok"
        
    except ImportError:
        logger.error("pyngrok not installed. Run: pip install pyngrok")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error opening ngrok tunnel: {e}")
        sys.exit(1)

def run_cloudflare(port):
    try:
        from pycloudflared import try_cloudflare
        
        logger.info(f"Opening Cloudflare tunnel to localhost:{port}...")
        # try_cloudflare returns a Popen object, but we want the URL
        # The library prints the URL to stdout, so we need to capture it or just let it print
        # However, try_cloudflare from pycloudflared is a context manager or simple function?
        # Let's check how pycloudflared works. It's a wrapper around the binary.
        # Actually pycloudflared.try_cloudflare is a function that runs the binary and returns the tunnel object.
        
        tunnel_url = try_cloudflare(port=port, verbose=False)
        return tunnel_url.tunnel, "Cloudflare"

    except ImportError:
        logger.error("pycloudflared not installed. Run: pip install pycloudflared")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error opening Cloudflare tunnel: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Expose local service via Ngrok or Cloudflare")
    parser.add_argument("--provider", choices=['ngrok', 'cloudflare'], default='cloudflare', 
                        help="Tunnel provider (default: cloudflare)")
    parser.add_argument("--port", type=int, help="Port to expose (default: from .env or 8000)")
    
    args = parser.parse_args()
    
    # Get port
    if args.port:
        APP_PORT = args.port
    else:
        from dotenv import load_dotenv
        load_dotenv()
        APP_PORT = int(os.getenv("APP_PORT", "8000"))

    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║       Retail Analytics System - Public Access            ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    try:
        if args.provider == 'ngrok':
            url, provider = run_ngrok(APP_PORT)
            message = ""
        else:
            url, provider = run_cloudflare(APP_PORT)
            message = "(Cloudflare Quick Tunnels do not require authentication)"
            
        print(f"\n✅ {provider.upper()} PUBLIC URL GENERATED SUCCESSFULLY:\n")
        print(f"   👉  {url}  👈")
        print(f"\n   (Share this URL with your friend for their Flutter app)")
        if message:
            print(f"   {message}")
        print(f"   (Press Ctrl+C to stop sharing)\n")
        
        # Keep alive
        if args.provider == 'ngrok':
             from pyngrok import ngrok
             # Create a signal handler
             def signal_handler(sig, frame):
                print("\nClosing tunnel...")
                ngrok.kill()
                sys.exit(0)
             signal.signal(signal.SIGINT, signal_handler)
             signal.pause()
        else:
            # For cloudflare, the thread/process is managed by pycloudflared usually
            # But try_cloudflare might return.
            # If pycloudflared.try_cloudflare runs a subprocess, we need to keep main thread alive.
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping...")
                sys.exit(0)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
