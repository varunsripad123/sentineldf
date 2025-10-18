# 🎨 SentinelDF Interactive GUI User Guide

Beautiful web-based interface for scanning files with drag-and-drop, real-time visualization, and one-click reports!

---

## 🚀 Quick Start

### Launch the GUI

```bash
# With API key flag
sentineldf gui --api-key YOUR_KEY

# Or use environment variable
export SENTINELDF_API_KEY=YOUR_KEY
sentineldf gui

# Custom port (default: 5050)
sentineldf gui --port 8080

# Without auto-opening browser
sentineldf gui --no-browser
```

The GUI will automatically open in your default browser at `http://localhost:5050`

---

## ✨ Key Features

### 1. **Drag & Drop File Uploads** 📤
- Drag files directly from your file explorer
- Drop them onto the upload zone
- Multiple files supported at once
- Instant scanning starts automatically

### 2. **Folder Scanning** 📁
- Enter any folder path
- Recursive scanning supported
- Scans all supported file types
- Real-time progress tracking

### 3. **Real-Time Visualization** 📊
- Live stats dashboard
- Total files scanned
- Safe vs Quarantined breakdown
- Average risk score
- Animated progress bar

### 4. **Interactive Results** 🔍
- Beautiful card-based layout
- Color-coded by threat level:
  - 🟢 **Green** - Safe files (risk < 30)
  - 🟡 **Yellow** - Medium risk (30-70)
  - 🔴 **Red** - High risk/Quarantined (> 70)
- Expandable threat details
- Signal strength indicators

### 5. **Quarantine Review** ⚠️
- Clearly marked quarantined files
- Detailed threat reasons
- Risk score with visual indicator
- Signal breakdown per threat type

### 6. **One-Click Downloads** 📄
- **HTML Report** - Beautiful formatted report
- **JSON Report** - Raw data for automation
- Reports include all scan details
- Timestamped for tracking

---

## 🎯 How to Use

### Upload Files

**Option 1: Drag & Drop**
1. Drag files from your computer
2. Drop them onto the purple upload zone
3. Watch the magic happen! ✨

**Option 2: Click to Browse**
1. Click anywhere on the upload zone
2. Select files from the file picker
3. Multiple selection supported

### Scan a Folder

1. Enter the full folder path in the text field
2. Example: `C:\Users\YourName\Documents\training_data`
3. Click "Scan Folder" button
4. Recursive scanning automatically enabled

### View Results

**Stats Dashboard:**
- **Total Files** - How many files were scanned
- **Safe** - Files that passed all checks (green)
- **Quarantined** - Files flagged as threats (red)
- **Avg Risk** - Average risk score across all files

**Individual Results:**
Each file card shows:
- **Filename** - Name of the scanned file
- **Status Badge** - ✅ SAFE or 🚨 QUARANTINED
- **Risk Score** - 0-100 scale with color coding
- **Threat Reasons** - Why it was flagged (if applicable)
- **Signal Analysis** - Breakdown of threat signals:
  - Prompt injection detection
  - Data poisoning indicators
  - SQL injection patterns
  - XSS attack vectors
  - And more...

### Download Reports

After scanning:
1. Two buttons appear: "Download HTML Report" and "Download JSON Report"
2. Click either to download instantly
3. Reports saved with timestamp in filename
4. Open HTML report in browser for beautiful visualization
5. Use JSON for automation/integration

---

## 🎨 UI Guide

### Color Coding

**Risk Levels:**
- **0-29 (Low)** 🟢 Green - Safe for use
- **30-69 (Medium)** 🟡 Orange - Review recommended
- **70-100 (High)** 🔴 Red - Quarantined/Dangerous

**Status Badges:**
- **✅ SAFE** - Green badge, passed all checks
- **🚨 QUARANTINED** - Red badge, contains threats

**Signal Strength:**
- **Red** - High confidence threat (>70%)
- **Orange** - Medium confidence (30-70%)
- **Green** - Low/no threat (<30%)

### Animations

- Cards **slide in** when results load
- Progress bar **fills smoothly** during scans
- Stats **scale up** with bounce effect
- Toast notifications **slide from right**
- Hover effects on **all interactive elements**

---

## 📊 Understanding Results

### Risk Score

**What it means:**
- **0-20** - Clean, no threats detected
- **21-40** - Minor concerns, likely false positives
- **41-60** - Suspicious patterns, review recommended
- **61-80** - High probability of threats
- **81-100** - Confirmed threats, quarantine immediately

### Threat Signals

**Common signals:**
- **prompt_injection** - Attempts to manipulate AI behavior
- **data_poisoning** - Malicious training data
- **sql_injection** - Database attack patterns
- **xss_attack** - Cross-site scripting attempts
- **command_injection** - System command exploits
- **backdoor_pattern** - Hidden malicious code

Each signal shows a **percentage (0-100%)** indicating confidence level.

### Quarantine Status

Files are quarantined if:
- Risk score ≥ 70
- Multiple high-confidence signals
- Known attack patterns detected
- Suspicious payload combinations

**Manual Review:**
- Check threat reasons carefully
- Review signal breakdown
- Verify if legitimate use case
- Contact support if unsure

---

## 💡 Pro Tips

### 1. Batch Processing
Upload multiple files at once for faster scanning:
- Drag 100+ files
- All scanned in single batch
- Parallel processing
- Progress tracked live

### 2. Folder Organization
Organize files before scanning:
- Group similar content
- Separate trusted vs untrusted sources
- Use subfolders for categories
- Easier report analysis

### 3. Regular Scanning
Make scanning a habit:
- Scan new data before training
- Weekly security audits
- Pre-deployment checks
- After data acquisition

### 4. Report Archives
Keep reports for compliance:
- Download JSON for records
- HTML for sharing with team
- Track improvements over time
- Audit trail for compliance

### 5. Integration Workflow
Use GUI for exploration, CLI for automation:
- GUI - Interactive review and learning
- CLI - Automated pipelines and CI/CD
- Both use same backend API
- Consistent results

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Use different port
sentineldf gui --port 5051
```

### Browser Doesn't Open
```bash
# Open manually
sentineldf gui --no-browser
# Then visit: http://localhost:5050
```

### Upload Fails
- Check file size (max 100MB per file)
- Ensure text files (binary not supported)
- Verify internet connection
- Check API key is valid

### Slow Scanning
- Large files take longer
- Many files process in batches
- Network speed affects API calls
- Try smaller batches if needed

### Results Not Showing
- Check browser console (F12)
- Verify API key is correct
- Ensure backend is reachable
- Try refreshing page

---

## 🎯 Use Cases

### 1. **Data Science Teams**
- Review dataset quality before training
- Identify poisoned samples
- Clean training data
- Compliance audits

### 2. **Security Researchers**
- Analyze suspicious files
- Test attack patterns
- Document threats
- Share findings (HTML reports)

### 3. **ML Engineers**
- Pre-training data validation
- Model input sanitization
- Production data monitoring
- Quality assurance

### 4. **Compliance Officers**
- Generate audit reports
- Track data quality
- Regulatory compliance
- Security documentation

### 5. **Developers**
- Test user inputs
- Validate API payloads
- Security testing
- Integration testing

---

## 📚 Keyboard Shortcuts

- **Ctrl/Cmd + Click** - Upload zone triggers file picker
- **Drag Files** - From any file explorer
- **F12** - Open browser dev tools (debugging)
- **Ctrl/Cmd + R** - Refresh page (clears results)
- **Esc** - Close toast notifications

---

## 🎨 Screenshots

### Main Interface
- **Upload Zone** - Drag & drop area with animations
- **Stats Dashboard** - Real-time metrics
- **Results View** - Color-coded threat cards

### After Scanning
- **Completed Stats** - All metrics populated
- **Download Buttons** - Report export options
- **Detailed Results** - Expandable threat info

### Quarantine Review
- **Red Flagged Files** - Clear visual warnings
- **Threat Breakdown** - Detailed reasons
- **Signal Analysis** - Confidence indicators

---

## 🚀 Advanced Usage

### Custom API Endpoint

Set custom backend URL:
```bash
export SENTINELDF_API_URL=https://your-api.com
sentineldf gui
```

### Automation Integration

Use GUI for initial review, then automate:
```python
from sentineldf import SentinelDF

# After GUI review, automate with CLI/SDK
client = SentinelDF(api_key="YOUR_KEY")
results = client.scan(approved_files)
```

### Team Sharing

Share scan results with team:
1. Download HTML report
2. Share via email/Slack
3. Recipients can view without API key
4. Beautiful formatting preserved

---

## 🎊 Tips for Impressive Demos

1. **Prepare Sample Files**
   - Mix safe and malicious samples
   - Show diverse threat types
   - Use realistic filenames

2. **Highlight Features**
   - Start with drag & drop
   - Show real-time progress
   - Download report at end

3. **Explain Results**
   - Point out color coding
   - Explain signal meanings
   - Show quarantine reasons

4. **Compare Options**
   - Demo GUI vs CLI
   - Show automation potential
   - Highlight ease of use

---

## 💬 Support

**Need Help?**
- 📧 Email: support@sentineldf.com
- 📚 Docs: https://docs.sentineldf.com
- 💬 Discord: https://discord.gg/sentineldf
- 🐙 GitHub: https://github.com/varunsripad123/sentineldf

---

## 🎉 Have Fun Scanning!

The GUI is designed to make security scanning **enjoyable** and **intuitive**.

**Remember:**
- Scan early, scan often
- Review quarantined files carefully
- Keep reports for compliance
- Share knowledge with your team

**Happy scanning!** 🛡️✨
