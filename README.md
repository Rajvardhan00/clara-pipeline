# Clara Answers — Automation Pipeline

> Converts call transcripts into AI voice agent configurations. Automatically.

---

## What This Does

| Input | Output |
|-------|--------|
| Demo call transcript | Account Memo JSON (v1) + Retell Agent Spec (v1) |
| Onboarding call transcript | Updated Memo (v2) + Agent Spec (v2) + Changelog |

---

## Folder Structure

```
clara_pipeline/
├── scripts/
│   ├── run_pipeline.py         ← Main runner (start here)
│   ├── extractor.py            ← Pulls structured data from transcripts
│   ├── prompt_generator.py     ← Builds Clara's voice agent prompt
│   ├── onboarding_updater.py   ← Merges onboarding changes, creates changelog
│   └── storage.py              ← Saves/loads all output files
├── workflows/
│   └── clara_n8n_workflow.json ← n8n workflow (import into n8n UI)
├── sample_data/
│   ├── demo_001.txt            ← BlazeSafe Fire Protection demo
│   ├── demo_002.txt            ← ShieldAlarm demo
│   ├── demo_003.txt            ← VoltGuard Electrical demo
│   ├── demo_004_005.txt        ← ArcticFlow + SafeNet demos
│   ├── onboarding_001_002_003.txt
│   └── onboarding_004_005.txt
├── outputs/
│   └── accounts/
│       └── 001/
│           ├── v1/
│           │   ├── account_memo.json
│           │   └── agent_spec.json
│           ├── v2/
│           │   ├── account_memo.json
│           │   └── agent_spec.json
│           ├── changelog.md
│           └── changelog.json
├── setup.bat                   ← Windows one-click setup
├── requirements.txt
└── README.md
```

---

## Quick Start (Windows)

### Step 1 — Get a FREE Gemini API Key

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (looks like: `AIzaSy...`)


---

### Step 2 — Run Setup

Double-click `setup.bat` OR open a terminal and run:

```bat
cd clara_pipeline
setup.bat
```

This installs the Python `google-generativeai` library.

---

### Step 3 — Set Your API Key

Open a terminal (Command Prompt or PowerShell) and run:

```bat
set GEMINI_API_KEY=your_actual_key_here
```


---

### Step 4 — Run the Full Pipeline

```bat
cd scripts
python run_pipeline.py
```

This will:
- Process all 5 demo transcripts → generate v1 memo + agent spec for each account
- Process all 5 onboarding transcripts → generate v2 memo + agent spec + changelog

---

### Step 5 — Check Your Outputs

All outputs saved to `outputs/accounts/<account_id>/`

```
outputs/accounts/001/v1/account_memo.json    ← Extracted business data
outputs/accounts/001/v1/agent_spec.json      ← Clara's voice agent config
outputs/accounts/001/v2/account_memo.json    ← Updated after onboarding
outputs/accounts/001/v2/agent_spec.json      ← Updated agent config
outputs/accounts/001/changelog.md            ← What changed and why
```

---

## Running Individual Pipelines

**Pipeline A only (demo → v1):**
```bat
python run_pipeline.py demo ../sample_data/demo_001.txt 001
```

**Pipeline B only (onboarding → v2):**
```bat
python run_pipeline.py onboarding ../sample_data/onboarding_001_002_003.txt
```

**Show summary of all processed accounts:**
```bat
python run_pipeline.py summary
```

---

## Using Your Own Transcripts

### Option A — Drop in transcript files

1. Save your transcript as a `.txt` file in `sample_data/`
2. Make sure the file header includes: `Account 001` or similar
3. Run: `python run_pipeline.py demo ../sample_data/your_file.txt`

### Option B — Multiple transcripts in one file

Separate each transcript with a line containing only `---`

```
TRANSCRIPT - Account 006
...transcript text...

---

TRANSCRIPT - Account 007
...transcript text...
```

### Option C — Audio recordings

1. Transcribe using [Whisper](https://github.com/openai/whisper) (free, local):
   ```bat
   pip install openai-whisper
   whisper your_audio.mp3 --output_format txt
   ```
2. Use the resulting `.txt` file as input

---

## n8n Workflow Setup (Optional Visual Orchestration)

If you want to use n8n instead of running Python directly:

### Install n8n (free, local):
```bat
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

### Import the workflow:
1. Open http://localhost:5678 in your browser
2. Click **Workflows** → **Import from file**
3. Select `workflows/clara_n8n_workflow.json`
4. Add your `GEMINI_API_KEY` as an environment variable in n8n settings
5. Click **Execute Workflow**

---

## Output Format: Account Memo JSON

```json
{
  "account_id": "001",
  "company_name": "BlazeSafe Fire Protection",
  "business_hours": {
    "days": "Monday-Friday",
    "start": "08:00",
    "end": "17:00",
    "timezone": "Central"
  },
  "emergency_definition": [
    "Sprinkler head leaking or burst",
    "Fire alarm going off",
    "Active water or fire"
  ],
  "emergency_routing_rules": {
    "primary": {"name": "Dispatch", "phone": "214-555-0101"},
    "secondary": {"name": "On-call technician", "phone": "214-555-0199"}
  },
  "questions_or_unknowns": [],
  "_meta": {"version": "v1", "generated_at": "..."}
}
```

---

## Output Format: Agent Spec JSON

```json
{
  "agent_name": "BlazeSafe Fire Protection - Clara",
  "voice_style": "professional-warm-female",
  "version": "v1",
  "system_prompt": "You are Clara, the virtual assistant for BlazeSafe Fire Protection...",
  "call_transfer_protocol": {
    "step1": "Transfer to dispatch at 214-555-0101, wait 30 seconds",
    "step2": "If no answer, try on-call tech at 214-555-0199",
    "final_fallback": "Apologize and promise callback within 15 minutes"
  }
}
```

---

## Architecture & Data Flow

```
Transcript (.txt)
       │
       ▼
[Extractor] ──── Gemini API ────► Account Memo JSON (v1)
       │                                   │
       │                                   ▼
       │                        [Prompt Generator] ──► Agent Spec JSON (v1)
       │                                   │
       │                                   ▼
       │                         Saved to outputs/
       │
       ▼ (onboarding transcript)
[Onboarding Updater] ── Gemini ──► v2 Memo + Changelog + v2 Agent Spec
```

---

## Known Limitations

- Gemini free tier has rate limits (~15 requests/minute). Pipeline includes 2-second delays between calls.
- If a transcript has very little information, some fields will be `null` — this is intentional (no hallucination).
- Audio transcription requires Whisper installed locally.
- n8n workflow is a reference implementation; file paths may need adjustment for your Docker volume.

---

## What I Would Improve With Production Access

1. **Retell API integration** — automatically create/update agents via Retell's API instead of manual import
2. **Webhook triggers** — n8n listens for new file uploads automatically
3. **Supabase storage** — replace file storage with a proper database for querying
4. **Asana task creation** — auto-create onboarding tasks when a new account is processed
5. **Diff viewer UI** — web page showing v1 vs v2 side by side with highlights
6. **Batch metrics dashboard** — Google Sheets with processing status for all accounts

---

## Submission Checklist

- [x] Pipeline A: demo → v1 memo + agent spec
- [x] Pipeline B: onboarding → v2 memo + agent spec + changelog
- [x] All 5 demo accounts processed
- [x] All 5 onboarding updates applied
- [x] Versioned outputs (v1/ and v2/ folders)
- [x] Changelog per account (`.md` and `.json`)
- [x] n8n workflow JSON export
- [x] Zero cost (Gemini free tier only)
- [x] Reproducible from README
- [x] No hallucination — missing data flagged in `questions_or_unknowns`
