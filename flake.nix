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
            echo "Python: $(python --version)"
            echo "Redis:  $(redis-server --version)"
            
            # Start Redis in the background if it's not running
            if ! redis-cli ping > /dev/null 2>&1; then
              echo "Starting local Redis instance..."
              redis-server --daemonize yes
            fi
            
            export GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)
            echo "Environment ready."
            # Automatically export the key from your .env file into the Nix shell environment
            if [ -f .env ]; then
              export $(grep -v '^#' .env | xargs)
              # Ensure the SDK sees the specific name it wants
              export GOOGLE_API_KEY=$GEMINI_API_KEY
            fi
              echo "✅ Environment variables loaded for google-genai."
          '';
        };
      });
}
