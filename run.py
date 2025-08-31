import os
import sys

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from main import AuPoSoNeOrchestrator


def main():
    try:
        print("Starting AuPoSoNe automation...")

        orchestrator = AuPoSoNeOrchestrator()
        orchestrator.process_clips("Valorant")

        print("✅ Automation completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
