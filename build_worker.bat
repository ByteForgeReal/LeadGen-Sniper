@echo off
echo Building LeadGen-Sniper Enrichment Worker...
cl /O2 /EHsc src/enrichment_worker.cpp /Fe:src/enrichment_worker.exe
if %errorlevel% neq 0 (
    echo [!] Build failed. Ensure MSVC compiler is in PATH.
    pause
    exit /b %errorlevel%
)
echo [√] Build successful: src/enrichment_worker.exe
del src\*.obj
pause
