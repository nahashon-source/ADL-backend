#!/bin/bash
cd ~/Desktop/ADL-backend

echo "Creating placeholder files with boilerplate..."

# --- main.py ---
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ADL Backend")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
EOF

echo "✅ Boilerplate files created successfully!"
