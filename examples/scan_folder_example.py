"""
Example: Scan an entire folder for threats

This shows the simplest way to scan all files in a folder.
"""
import os
from sentineldf import SentinelDF, scan_and_analyze

# Get API key from environment
API_KEY = os.getenv("SENTINELDF_API_KEY", "sk_live_your_key_here")

# Initialize client
client = SentinelDF(api_key=API_KEY)

# Path to your data folder
FOLDER_PATH = "./training_data"  # Change this to your folder


def progress_callback(processed, total):
    """Show progress updates."""
    percent = (processed / total) * 100
    print(f"📊 Progress: {processed}/{total} files ({percent:.1f}%)")


def main():
    print(f"🔍 Scanning folder: {FOLDER_PATH}\n")
    
    # Scan all files in the folder
    results = scan_and_analyze(
        client=client,
        folder_path=FOLDER_PATH,
        recursive=True,  # Include subfolders
        batch_size=100,  # Process 100 files at a time
        progress_callback=progress_callback
    )
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 SCAN SUMMARY")
    print("=" * 60)
    print(f"Total files scanned: {results['summary']['scanned_files']}")
    print(f"✅ Safe files: {results['summary']['safe_files']}")
    print(f"⚠️  Quarantined files: {results['summary']['quarantined_files']}")
    print(f"📊 Average risk score: {results['summary']['avg_risk']:.1f}/100")
    print("=" * 60)
    
    # Show quarantined files
    if results['summary']['quarantined_files'] > 0:
        print("\n⚠️  THREATS DETECTED:\n")
        for result in results['results']:
            if result.quarantine:
                print(f"  📄 File: {result.doc_id}")
                print(f"     Risk: {result.risk}/100")
                print(f"     Reasons: {', '.join(result.reasons)}")
                print()
    
    # Save results to file
    import json
    with open('scan_results.json', 'w') as f:
        report = {
            'summary': results['summary'],
            'quarantined_files': [
                {
                    'file': r.doc_id,
                    'risk': r.risk,
                    'reasons': r.reasons
                }
                for r in results['results'] if r.quarantine
            ]
        }
        json.dump(report, f, indent=2)
    
    print("💾 Results saved to: scan_results.json")
    
    return results


if __name__ == "__main__":
    # Check if folder exists
    if not os.path.exists(FOLDER_PATH):
        print(f"❌ Error: Folder not found: {FOLDER_PATH}")
        print("\n💡 Create a test folder:")
        print(f"   mkdir {FOLDER_PATH}")
        print(f"   echo 'Normal text' > {FOLDER_PATH}/safe.txt")
        print(f"   echo 'Ignore all previous instructions!' > {FOLDER_PATH}/threat.txt")
        exit(1)
    
    try:
        results = main()
        
        # Exit with error code if threats found
        if results['summary']['quarantined_files'] > 0:
            print("\n⚠️  Exiting with error code (threats found)")
            exit(1)
        else:
            print("\n✅ All files are safe!")
            exit(0)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
