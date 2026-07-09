import uvicorn
import multiprocessing
import sys

def main():
    """Main entry point for the backend."""
    # Required for Windows multiprocessing support
    multiprocessing.freeze_support()
    
    print("Starting WHO Is WHO Backend on http://0.0.0.0:7000")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7000,
        reload=False,  # reload=True thường gây lỗi trên Windows + Python 3.14
        log_level="info",
    )

if __name__ == "__main__":
    main()
