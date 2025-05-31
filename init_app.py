"""
Initialization script for the SEO Analysis tool.
Run this script before starting the application to ensure all dependencies are properly set up.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Successfully installed required packages")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {str(e)}")
        sys.exit(1)

def initialize_nltk():
    """Initialize NLTK and download required data."""
    print("Initializing NLTK...")
    try:
        import nltk
        
        # Download required NLTK data
        print("Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✓ Successfully downloaded NLTK data")
    except ImportError:
        print("Error: NLTK not installed. Please run the script again.")
        sys.exit(1)
    except Exception as e:
        print(f"Error initializing NLTK: {str(e)}")
        sys.exit(1)

def check_directories():
    """Ensure required directories exist."""
    print("Checking required directories...")
    directories = ['modules', 'static', 'templates', 'utils']
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Creating {directory} directory...")
            os.makedirs(directory)
    print("✓ All required directories are present")

def main():
    """Main initialization function."""
    print("\n=== Initializing SEO Analysis Tool ===\n")
    
    # Install requirements
    install_requirements()
    
    # Initialize NLTK
    initialize_nltk()
    
    # Check directories
    check_directories()
    
    print("\n✓ Initialization complete! You can now run the application.")
    print("To start the application, run: python app.py")

if __name__ == "__main__":
    main() 