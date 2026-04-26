{
  description = "Syllabus Agent API Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonEnv = pkgs.python312Packages;
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Base Language
            python312
            
            # FastAPI & Server
            pythonEnv.fastapi
            pythonEnv.uvicorn
            pythonEnv.python-multipart # Required for -F (File) uploads
            pythonEnv.pyyaml
            
            # AI & Logic
            pythonEnv.google-genai
            pythonEnv.python-dotenv
            pythonEnv.pypdf            # For PDF extraction
            
            # State Management
            pythonEnv.redis
            redis                      # The actual redis-server binary
          ];

            shellHook = ''
            echo "--- Syllabus Agent Shell ---"
            
            # Define exact paths relative to the flake root
            SECRET_FILE="./agent-api/secrets.yaml"
            ENV_FILE="./agent-api/.env"

            if [ -f "$SECRET_FILE" ]; then
              echo "🔓 Decrypting $SECRET_FILE into $ENV_FILE..."
              
              # Extract the specific key and save to the .env file
              sops -d --extract '["google_secrets"]' "$SECRET_FILE" > "$ENV_FILE"
              
              # Load the variables into the current shell session
              export $(grep -v '^#' "$ENV_FILE" | xargs)
              export GOOGLE_API_KEY=$GEMINI_API_KEY
              
              echo "✅ Environment variables loaded for agent-api."
            else
              echo "⚠️ No secrets.yaml found at $SECRET_FILE."
              echo "Current directory is: $(pwd)"
            fi
            # Start Redis Logic...
            if ! redis-cli ping > /dev/null 2>&1; then
              redis-server --daemonize yes
            fi
          '';
        };
      });
}
