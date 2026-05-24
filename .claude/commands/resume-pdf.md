Generate a PDF of the resume with real PII included.

## How it works

`_data/pii.example.yml` uses `# pii: <description>` inline comments to mark every field that was redacted for the public site. The fields are `last_name`, `email`, `phone`, `address`, and `linkedin`. The first name comes from `_config.yml` and is already public. This skill:
1. Scans `_data/pii.example.yml` for `# pii:` markers
2. Asks you for the real value of each field
3. Writes them to `_data/pii.yml` (gitignored — never committed)
4. Runs `rake pdf` to produce `resume.pdf`

## Execution steps

**Step 1 — discover fields**

Read `_data/pii.example.yml` with the Read tool. For each line that contains `# pii:`, extract:
- The YAML key (the word before the `:` on that line)
- The description (text after `# pii:`)
- Whether the field is optional (description contains "optional")

**Step 2 — collect values**

Check whether `_data/pii.yml` already exists with the Read tool.
- If it exists, ask the user (via AskUserQuestion): "A `_data/pii.yml` already exists. Use the saved values or re-enter them?" with options "Use existing values" / "Re-enter all values".
- If the user chooses to use existing values, skip to Step 3.

Otherwise, use AskUserQuestion to collect values. Group up to 4 fields per call. For each field, the question should be "What is your <description>?" with options:
- `"Enter value"` — description: "Type the real value in the Other field"
- `"Leave blank"` — description: "Omit this field from the PDF" (only show for optional fields)

Record each value from the user's Other input (or mark as omitted if they chose "Leave blank").

**Step 3 — write `_data/pii.yml`**

Write `_data/pii.yml` using the Write tool. Build the YAML content from the collected values, preserving the same key order as the example file. Omit any fields the user left blank. Do not include the `# pii:` comments in the output file.

**Step 4 — generate PDF**

Run `rake pdf` via Bash. This builds the site and uses headless Chrome to export `resume.pdf`.

If the command fails, report the error and offer to leave `_data/pii.yml` in place so the user can retry manually with `rake pdf`.

**Step 5 — confirm**

Confirm that `resume.pdf` exists and report its path. Do not delete `_data/pii.yml` — it is gitignored and safe to keep for future runs.
