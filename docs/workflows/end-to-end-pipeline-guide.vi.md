# Huong dan chay News-to-Video Pipeline tu dau den cuoi

Tai lieu nay ghi lai tinh trang hien tai cua project `hyperframevideo` va cach tu chay pipeline tu luc co tin tuc dau vao den luc co video MP4. Pipeline hien tai la local-first: repo tu quan ly artifact, timing, storyboard, composition va render; ChatGPT chi nen dung de viet hoac sua noi dung `SCRIPT.md`.

## 1. Tinh trang project hien tai

Project dang co CLI Python ten `hyperframe-video`, chay bang `uv`.

Kiem tra ngay 2026-06-09:

- Test suite: `114 passed`.
- CLI co cac lenh chinh: direct URL, `--discover`, `--voiceover`, `--storyboard`, `--compose`, `--render`.
- Thu muc production run nam trong `.runs/<run-id>/`.
- Trong workspace hien co cac run mau:
  - `.runs/manual-test-01`: da co `source-evidence.json`, `SELECTED_STORY.md`, `SCRIPT.md`.
  - `.runs/manual-voice-test`: da co voiceover.
  - `.runs/tin-ai`: da co `SCRIPT.md`, `voiceover.json`, `STORYBOARD.md`, `composition/index.html` va render cache, nhung chua thay `output.mp4` o root run.
- May hien tai co `node` va `npx`, nhung chua co `ffmpeg` tren `PATH`, nen buoc render MP4 se fail cho toi khi cai FFmpeg.
- Worktree dang co thay doi san o `CONTEXT.md`, `src/hyperframevideo/cli.py`, `tests/test_cli.py`, va mot vai file chua track. Khong can dong vao cac file nay de chay pipeline.

## 2. Chuan bi moi truong

Mo PowerShell tai root repo:

```powershell
cd D:\Workspace\hyperframevideo
```

Kiem tra Python dependencies va test:

```powershell
uv run pytest
uv run hyperframe-video --help
```

Neu muon render MP4, may can co:

- Node.js 22+.
- `npx`.
- FFmpeg tren `PATH`.

Kiem tra:

```powershell
node --version
npx --version
ffmpeg -version
```

Neu `ffmpeg` bao khong tim thay, cai FFmpeg va mo lai terminal de `PATH` cap nhat.

## 3. Tong quan artifact trong mot Production Run

Mot run day du se co dang:

```text
.runs/<run-id>/
|-- candidates.json           # chi co neu dung --discover
|-- source-evidence.json      # du lieu fact-grounded lay tu source
|-- SELECTED_STORY.md         # tom tat story duoc chon
|-- SCRIPT.md                 # ban script do ban/ChatGPT viet, can approve thu cong
|-- voiceover.json            # manifest timing va audio
|-- voiceover/
|   |-- segment-001.wav
|   `-- segment-002.wav
|-- STORYBOARD.md             # storyboard sinh tu script + voiceover timing
|-- composition/
|   |-- index.html
|   `-- voiceover/
`-- output.mp4                # video sau render thanh cong
```

Nguyen tac quan trong:

- `source-evidence.json` la nguon su that cho script.
- `SCRIPT.md` la file duy nhat ban dua cho ChatGPT sinh/sua.
- Khong de ChatGPT sinh `STORYBOARD.md`, `composition/index.html`, HTML, shot list, animation plan, hay HyperFrames code.
- Cac lenh downstream chi chay khi `SCRIPT.md` co `Status: approved`.
- Nhieu lenh se tu choi overwrite artifact da ton tai de tranh dung du lieu cu sai.

## 4. Cach chay tu mot URL cu the

Chon mot `run-id` ngan, khong trung voi thu muc da co trong `.runs`.

```powershell
uv run hyperframe-video --run-id demo-001 "https://techcrunch.com/2026/06/07/openai-is-still-working-on-that-super-app/"
```

Sau lenh nay, kiem tra:

```powershell
Get-ChildItem .runs\demo-001
```

Ban se thay toi thieu:

- `source-evidence.json`
- `SELECTED_STORY.md`
- `SCRIPT.md`

`SCRIPT.md` luc nay chi la draft placeholder. Viec tiep theo la dung ChatGPT de viet lai script dua tren evidence.

## 4A. Cach chay orchestrator voi DeepSeek

Neu da co `DEEPSEEK_API_KEY`, co the dung orchestrator de tao `SCRIPT.md` bang DeepSeek va dung o cong **Script Approval**:

```powershell
$env:DEEPSEEK_API_KEY = "your-api-key"
uv run hyperframe-video run --url "https://example.com/news-story" --run-id demo-001 --script-provider deepseek --language vi
```

Tuy chon DeepSeek:

```powershell
$env:DEEPSEEK_BASE_URL = "https://api.deepseek.com"
$env:DEEPSEEK_MODEL = "deepseek-chat"
uv run hyperframe-video run --url "https://example.com/news-story" --run-id demo-001 --script-provider deepseek --language vi --script-model deepseek-reasoner
```

Mac dinh lenh nay ghi `progress.jsonl`, in progress dang text, va dung khi `SCRIPT.md` van la:

```text
Status: draft
```

Neu can JSONL cho automation:

```powershell
uv run hyperframe-video run --url "https://example.com/news-story" --run-id demo-001 --script-provider deepseek --language vi --progress-format jsonl
```

Neu muon batch trusted tu approve script moi draft va chay tiep toi compose:

```powershell
uv run hyperframe-video run --url "https://example.com/news-story" --run-id demo-001 --script-provider deepseek --language vi --auto-approve-script
```

Render van la opt-in:

```powershell
uv run hyperframe-video run --url "https://example.com/news-story" --run-id demo-001 --script-provider deepseek --language vi --auto-approve-script --render
```

Resume an toan: chay lai cung `--run-id` se skip artifact da co (`source-evidence.json`, `SCRIPT.md`, `voiceover.json`, `STORYBOARD.md`, `composition/`, `output.mp4`) va khong overwrite. Moi skip duoc ghi vao `.runs/<run-id>/progress.jsonl`.

Luu y: DeepSeek va cac Script Drafting Provider chi duoc tao hoac sua **Source-Grounded Script**. Khong dung provider de tao `STORYBOARD.md`, `composition/index.html`, voiceover manifest, hay render code.

Dung `--language vi` de sinh noi dung video tieng Viet, hoac `--language en` de sinh tieng Anh. Gia tri nay duoc dua vao Script Drafting Prompt va yeu cau DeepSeek ghi header `Language:` tuong ung trong `SCRIPT.md`.

## 5. Cach chay bang discovery

Neu chua co URL cu the, dung discovery:

```powershell
uv run hyperframe-video --run-id demo-ai --discover "latest AI product news" --candidates 5
```

CLI se tim candidate, hien danh sach va yeu cau chon mot bai. Sau khi chon, run se duoc tao trong `.runs/demo-ai/`.

Neu discovery khong tra ve ket qua tot, lay URL thu cong tu trinh duyet va chay theo cach direct URL o muc 4.

## 6. Prompt ChatGPT de viet `SCRIPT.md` lan dau

Mo file prompt co san:

```powershell
notepad docs\prompts\script-drafting.md
```

Copy toan bo noi dung trong block ```text```. Sau do mo:

```powershell
notepad .runs\demo-001\source-evidence.json
```

Copy toan bo JSON va dan vao cho `<PASTE SOURCE EVIDENCE HERE>` trong prompt.

Neu muon prompt gon hon de dan vao ChatGPT, dung mau nay:

```text
You are writing a short-form news video script for a local HyperFrames production pipeline.

Your job is to produce SCRIPT.md only. Do not produce a storyboard, animation plan, shot list, HTML, or HyperFrames code.

Use only the facts in the source evidence. Do not invent claims. Do not copy long passages from the source.

Tone:
- Curiosity-driven news explainer
- Smart, fast-paced, and clear
- Engaging without being sensational

Video constraints:
- Language: English unless I explicitly request another language
- Format: vertical short video
- Target duration: 60-90 seconds
- Visual Treatment: premium-news

Return exactly this Markdown structure:

Status: draft
Language: en
Target Duration: 60-90 seconds
Visual Treatment: premium-news

# Title

# Hook

# Source-Grounded Script

## Segment 1
Narration: ...
On-screen text: ...
Purpose: ...
Facts used:
- ...

Add as many segments as needed.

# Fact Check

- Claim: ...
  Source: ...

# Production Notes

Now write SCRIPT.md from this source evidence:

<paste the full source-evidence.json here>
```

Neu ban muon video tieng Viet, doi phan constraint thanh:

```text
- Language: Vietnamese
```

Va header output nen la:

```text
Language: vi
```

## 7. Lam gi voi script ChatGPT sinh ra

Sau khi ChatGPT tra ve Markdown:

1. Mo file run:

   ```powershell
   notepad .runs\demo-001\SCRIPT.md
   ```

2. Xoa toan bo noi dung placeholder cu.
3. Dan toan bo output cua ChatGPT vao file.
4. Giu dong dau la:

   ```text
   Status: draft
   ```

5. Doc lai va fact-check:
   - Moi claim quan trong co trong `source-evidence.json` khong?
   - Co cau nao nghe hay nhung khong co source khong?
   - `Narration:` co du ngan de doc thanh voiceover khong?
   - `On-screen text:` co ngan, ro, khong qua dai khong?
   - Cac segment co dung format `## Segment N` khong?

6. Khi da hai long, doi:

   ```text
   Status: draft
   ```

   thanh:

   ```text
   Status: approved
   ```

Chi approve sau khi ban da doc va chap nhan noi dung. Dong `Status: approved` la approval gate cho voiceover/storyboard/compose.

## 8. Prompt ChatGPT de sua script

Dung prompt sua script khi ban da co `SCRIPT.md` nhung can sua tone, do dai, ngon ngu, hoac facts.

Dan cho ChatGPT ca `SCRIPT.md` hien tai va `source-evidence.json`, roi dung prompt:

```text
You are editing SCRIPT.md for a local HyperFrames news-to-video pipeline.

Return the full corrected SCRIPT.md only.
Do not return explanations.
Do not create a storyboard, animation plan, shot list, HTML, or HyperFrames code.
Keep the required SCRIPT.md headings and fields exactly:
- Status
- Language
- Target Duration
- Visual Treatment
- # Title
- # Hook
- # Source-Grounded Script
- ## Segment N
- Narration
- On-screen text
- Purpose
- Facts used
- # Fact Check
- # Production Notes

Use only facts supported by the source evidence. Remove unsupported claims.

My requested changes:
- <write what you want changed, for example: make it Vietnamese, reduce to 6 segments, make on-screen text shorter, make the hook less sensational>

Current SCRIPT.md:

<paste current .runs/<run-id>/SCRIPT.md here>

Source evidence:

<paste .runs/<run-id>/source-evidence.json here>
```

Sau khi nhan ban sua:

1. Thay toan bo `.runs/<run-id>/SCRIPT.md` bang output moi.
2. Neu ban chua review xong, de `Status: draft`.
3. Khi da review xong, doi sang `Status: approved`.

Neu ban da tao voiceover/storyboard/composition truoc do ma lai sua `SCRIPT.md`, artifacts downstream co the khong con khop voi script. Cach an toan nhat la tao run moi voi `run-id` moi va chay lai tu dau. Neu muon dung lai run cu, can xoa cac artifact downstream cu truoc khi chay lai:

```text
.runs\<run-id>\voiceover.json
.runs\<run-id>\voiceover\
.runs\<run-id>\STORYBOARD.md
.runs\<run-id>\composition\
.runs\<run-id>\output.mp4
```

Chi xoa khi ban chac chan khong can giu ban cu.

## 9. Tao voiceover

Khi `SCRIPT.md` da co:

```text
Status: approved
```

Chay:

```powershell
uv run hyperframe-video --voiceover demo-001
```

Lenh nay:

- Doc moi dong `Narration:`.
- Tao audio `.wav` trong `.runs/demo-001/voiceover/`.
- Tao `voiceover.json` voi duration cua tung segment.

Neu gap loi:

- `SCRIPT.md not found`: sai `run-id` hoac run chua ton tai.
- `Status: draft`: ban chua approve script.
- `VieNeu SDK is not installed`: can cai/setup VieNeu runtime truoc khi tao voiceover.
- `Voiceover artifacts already exist`: run da co `voiceover.json` hoac `voiceover/`; tao run moi hoac xoa artifact cu neu muon chay lai.

## 10. Tao storyboard

Sau khi co `voiceover.json`, chay:

```powershell
uv run hyperframe-video --storyboard demo-001
```

Lenh nay tao:

```text
.runs\demo-001\STORYBOARD.md
```

Storyboard duoc sinh tu:

- `SCRIPT.md`
- `voiceover.json`
- timing cua audio

Khong sua storyboard bang ChatGPT tru khi ban biet ro minh dang lam gi. Storyboard la contract cho buoc compose.

## 11. Tao HyperFrames composition

Sau khi co `STORYBOARD.md`, chay:

```powershell
uv run hyperframe-video --compose demo-001
```

Lenh nay tao:

```text
.runs\demo-001\composition\index.html
.runs\demo-001\composition\voiceover\
```

Composition hien tai la HTML deterministic tu storyboard va treatment `premium-news`. Neu `composition/` da ton tai, lenh se fail de tranh overwrite.

## 12. Render MP4

Truoc khi render, dam bao `node`, `npx`, va `ffmpeg` deu chay duoc trong terminal.

```powershell
node --version
npx --version
ffmpeg -version
```

Sau do chay:

```powershell
uv run hyperframe-video --render demo-001
```

Neu thanh cong, output nam tai:

```text
.runs\demo-001\output.mp4
```

Neu bao thieu `ffmpeg`, cai FFmpeg va mo lai terminal. Neu bao `output.mp4 already exists`, tao run moi hoac xoa output cu neu muon render lai.

## 13. Checklist chay nhanh

Dung checklist nay cho moi video moi:

```powershell
cd D:\Workspace\hyperframevideo

uv run pytest

uv run hyperframe-video --run-id demo-001 "https://example.com/news-article"

# Dung ChatGPT tao/sua SCRIPT.md tu source-evidence.json
# Thay noi dung .runs\demo-001\SCRIPT.md
# Review fact va doi Status: draft -> Status: approved

uv run hyperframe-video --voiceover demo-001
uv run hyperframe-video --storyboard demo-001
uv run hyperframe-video --compose demo-001
uv run hyperframe-video --render demo-001
```

## 14. Cac loi thuong gap

`Production Run already exists`

Run ID da co trong `.runs`. Dung `run-id` moi, vi du `demo-002`.

`Status: draft`

Ban chua approve script. Mo `SCRIPT.md`, review, roi doi `Status: approved`.

`approved scripts without Narration lines`

ChatGPT sinh sai format hoac bo mat cac dong `Narration:`. Dua lai script cho ChatGPT sua theo prompt o muc 8.

`voiceover.json not found`

Ban chua chay `--voiceover`, hoac voiceover fail.

`STORYBOARD.md already exists`

Run da co storyboard. Neu script/voiceover da doi, tao run moi la cach sach nhat.

`composition/ already exists`

Run da compose roi. Tao run moi hoac xoa composition cu neu can compose lai.

`Missing required tools: ffmpeg`

Cai FFmpeg va dam bao `ffmpeg` nam tren `PATH`.

## 15. Ranh gioi viec nen giao cho ChatGPT

Nen giao cho ChatGPT:

- Viet moi `SCRIPT.md` tu `source-evidence.json`.
- Sua tone, do dai, ngon ngu, hook, segment, on-screen text trong `SCRIPT.md`.
- Rut gon hoac fact-check noi dung script dua tren evidence.

Khong nen giao cho ChatGPT:

- Tao `voiceover.json`.
- Tao `STORYBOARD.md`.
- Tao `composition/index.html`.
- Tao HyperFrames animation code cho repo nay.
- Sua artifact downstream sau khi pipeline da sinh ra, tru khi ban se chay lai tu dau.

Ly do: repo da co parser, approval gate, timing, storyboard planner, treatment config, composition generator va render command. Neu ChatGPT tu tao cac artifact downstream, chung de lech format va lam cac buoc sau fail.
