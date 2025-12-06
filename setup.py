"""
Nion Orchestration Engine - Quick Start Script
Helps setup and run the engine with proper environment configuration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def get_platform():
    """Get current platform"""
    return platform.system()


def check_python_version():
    """Check if Python 3.11+ is available"""
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ required. Current: {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_dependencies():
    """Check if required tools are available"""
    tools = {
        "pip": ["pip", "--version"],
        "git": ["git", "--version"],
    }

    print("\nChecking dependencies...")
    all_available = True
    
    for tool, cmd in tools.items():
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"✓ {tool} available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {tool} not found")
            all_available = False

    return all_available


def setup_venv():
    """Setup Python virtual environment"""
    print("\nSetting up virtual environment...")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    
    platform_name = get_platform()
    
    if platform_name == "Windows":
        pip_path = Path("venv\\Scripts\\pip")
    else:
        pip_path = Path("venv/bin/pip")
    
    try:
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def configure_environment():
    """Configure environment variables"""
    print("\nConfiguring environment variables...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("⚠ OPENAI_API_KEY not set")
        print("  Please set it with:")
        if get_platform() == "Windows":
            print("  $env:OPENAI_API_KEY = 'sk-your-api-key-here'")
        else:
            print("  export OPENAI_API_KEY='sk-your-api-key-here'")
        return False
    
    print(f"✓ OPENAI_API_KEY is set ({api_key[:20]}...)")
    return True


def run_test_local():
    """Run local test"""
    print("\nRunning local test...")
    print("-" * 50)
    
    platform_name = get_platform()
    
    if platform_name == "Windows":
        python_path = Path("venv\\Scripts\\python")
    else:
        python_path = Path("venv/bin/python")
    
    try:
        subprocess.run([str(python_path), "test_local.py"], check=False)
        return True
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def main():
    """Main setup function"""
    print("=" * 50)
    print("NION ORCHESTRATION ENGINE - SETUP")
    print("=" * 50)
    
    # Check Python
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("⚠ Some tools not available. Continuing anyway...")
    
    # Setup venv
    if not setup_venv():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Configure environment
    if not configure_environment():
        print("⚠ Environment not fully configured")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Run test
    print("\n" + "=" * 50)
    response = input("Run local test now? (y/n): ")
    if response.lower() == 'y':
        run_test_local()
    
    # Run server option
    print("\n" + "=" * 50)
    response = input("Start FastAPI server? (y/n): ")
    if response.lower() == 'y':
        platform_name = get_platform()
        if platform_name == "Windows":
            python_path = Path("venv\\Scripts\\python")
        else:
            python_path = Path("venv/bin/python")
        
        print("\nStarting server on http://localhost:8000...")
        print("Press Ctrl+C to stop")
        subprocess.run([
            str(python_path), "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    
    print("\n✓ Setup completed!")


if __name__ == "__main__":
    main()
