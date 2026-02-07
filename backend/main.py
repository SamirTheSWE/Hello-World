"""
The Main Running File
"""

import os
import uvicorn
from dotenv import load_dotenv

from src.app import HelloWorldApp


if __name__ == "__main__":
    if os.name == "nt":
        os.system("cls")

    env_files = [".env", ".env.production"]
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file)

    app = HelloWorldApp(
        debug=bool(os.environ.get('DEBUG', False)),
        root_path=os.environ.get('ROOT_PATH', None),
    )
    
    uvicorn.run(
        app,
        port=int(os.environ.get('PORT', 8080)),
        proxy_headers=True,
        forwarded_allow_ips=os.environ.get('FORWARDED_ALLOW_IPS', '127.0.0.1'),
    )
