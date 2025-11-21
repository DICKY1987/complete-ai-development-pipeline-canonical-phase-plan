# 0) Authenticate once (if needed)
# gh auth login

# 1) Generate the absolute-path variant from the relative plan
$dest = 'C:\Users\richg\HIGH_LEVEL_MOD_PLUGIN_DEV\AI_MANGER\AIDER_PROMNT&PLAN_REF'
New-Item -ItemType Directory -Path $dest -Force | Out-Null

# Read the existing relative plan
$plan = Get-Content .\plan\phase_plan.yaml -Raw

# Build a safe prefix for YAML (use forward slashes to avoid escaping issues)
$prefix = ([IO.Path]::TrimEndingDirectorySeparator($dest)) + [IO.Path]::DirectorySeparatorChar
$prefixFS = $prefix -replace '\\','/'  # e.g., C:/Users/.../AIDER_PROMNT&PLAN_REF/

# Replace each promptFile: prompts/xxx with a quoted absolute path
$absPlan = [regex]::Replace(
    $plan,
    '^(?<lead>\s*promptFile\s*:\s*)(?<rel>["'']?prompts/)(?<rest>[^"''\r\n]+)',
    { param($m) $m.Groups['lead'].Value + '"' + $prefixFS + $m.Groups['rest'].Value + '"' },
    [System.Text.RegularExpressions.RegexOptions]::Multiline
)

# Write the absolute-path plan
$absPlanPath = Join-Path $dest 'phase_plan.absolute.yaml'
Set-Content -Path $absPlanPath -Value $absPlan -Encoding UTF8

# 2A) Publish as a private Gist
gh gist create $absPlanPath `
  -d "QFT_updated: absolute-path phase plan (Aider prompts)" `
  -p -f "phase_plan.absolute.yaml"

# 2B) OR: Commit to the repo and open a PR
git checkout -b chore/abs-plan-variant
Copy-Item -Force $absPlanPath .\plan\phase_plan.absolute.yaml
git add .\plan\phase_plan.absolute.yaml
git commit -m "chore(plan): add absolute-path phase plan variant for Aider"
git push -u origin chore/abs-plan-variant
gh pr create `
  --title "chore(plan): add absolute-path plan variant" `
  --body "Adds plan/phase_plan.absolute.yaml pointing to $dest for local Aider runs; keeps portable plan unchanged." `
  --base main `
  --head chore/abs-plan-variant

# 3) Optional — Track with an Issue
gh issue create `
  --title "Adopt absolute-path plan for local Aider runs" `
  --body "Add and verify phase_plan.absolute.yaml; ensure CI ignores non-portable variant." `
  --label planning,docs
