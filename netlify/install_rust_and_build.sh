#!/usr/bin/env bash
set -e

# Install rustup (Rust toolchain) non-interactively
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Load cargo environment for the rest of the build
source "$HOME/.cargo/env"
export PATH="$HOME/.cargo/bin:$PATH"

# Ensure pip is up-to-date
python -m pip install --upgrade pip

# Now continue with the normal dependency install from moved file
python -m pip install -r frontend/requirements.txt

# Netlify normally handles the rest of the build or serving of static files,
# but since the backend is python (FastAPI), Netlify can only serve the `frontend` folder statically.
echo "Rust installed and Python deps installed."
