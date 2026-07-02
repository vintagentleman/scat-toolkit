# scat-toolkit

Tooling for the **SCAT corpus** — the *Санкт-Петербургский корпус агиографических текстов* (St Petersburg Corpus of Hagiographic Texts), a historical corpus of Old Russian / Church Slavonic hagiography (saints' *vitae* and encomia, 15th–17th c.) developed at the Department of Mathematical Linguistics, St Petersburg State University.

This repository holds the **processing tools**, not the texts. The corpus content itself — raw transliterated manuscripts and their morphological/structural annotation — lives in the companion repository [`scat-content`](https://github.com/vintagentleman/scat-content), included here as a git submodule.

The toolkit does three things, each as a small command-line program:

| Tool | Turns … | … into |
| --- | --- | --- |
| `tokenizer.py` | a raw transliterated manuscript | a token-per-line TSV skeleton |
| `converter.py` | a morphologically annotated TSV | normalised, lemmatised output in several formats |
| `annotator.py` | a tokenised text + a "precedent" store | a colour-coded `.xlsx` workbook for manual disambiguation |

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency and environment management.

Runtime dependencies (`click`, `lxml`, `pyyaml`, `xlsxwriter`) and development tools (`ruff`, `pytest`, `ty`, `pre-commit`) are declared in [`pyproject.toml`](pyproject.toml) and locked in `uv.lock`.

## Installation

```sh
git clone --recurse-submodules https://github.com/vintagentleman/scat-toolkit.git
cd scat-toolkit

uv sync
```

If you cloned without `--recurse-submodules`, pull the corpus content in afterwards:

```sh
git submodule update --init
```

The tools are run from the repository root through `uv run` (see [Usage](#usage)); each computes its own paths, and all output is written under a `generated/` directory that is created on demand and is git-ignored.

## Corpus layout

Under the `scat-content/` submodule:

- `raw/*.txt` — manuscripts in the project's 8-bit transliteration (CP866 / `IBM866`), obsolete Cyrillic graphemes mapped to Latin letters, with inline markers for superscripts `(…)`, titlo `#`, proper nouns `*`, and structural breaks.
- `annotation/morphological/*.tsv` — one token per line; column 0 is the surface form, columns 1–6 are positional grammemes whose meaning depends on the part-of-speech tag in column 1.
- `annotation/structural/*.txt` and `annotation/combined/*.tsv` — the same material with structural XML markup (`<head>`, `<div1 …>`) inlined.

## Usage

Run each tool from the repository root through the project environment — prefix with `uv run` as shown, or activate `.venv` and drop the prefix. Every tool accepts `--help`.

### 1. `tokenizer.py` — raw text → token skeleton

Splits a raw manuscript into one token per line, reassembling multi-piece tokens (scribal corrections, hanging punctuation, page/line breaks) and resolving numerals.

```sh
# tokenise every raw manuscript
uv run python src/tokenizer.py

# tokenise one file
uv run python src/tokenizer.py "DmPrlc.txt"
```

| Option | Default | Meaning |
| --- | --- | --- |
| `-p, --path` | `raw` | source directory, relative to `scat-content/` |
| `-e, --encoding` | `IBM866` | source-file encoding |
| `GLOB` (argument) | `*.txt` | which files to read |

Output: `generated/tokenizer/<manuscript>.tsv`.

### 2. `converter.py` — annotated TSV → normalised, lemmatised output

The main pipeline. For each token it normalises the orthography, computes the lemma (dispatched by part of speech), and serialises the result in the chosen format. Tokens whose lemma cannot be resolved are reported to the console.

```sh
# convert all morphological annotations to TEI XML (the default)
uv run python src/converter.py

# emit the tabular format instead
uv run python src/converter.py -m tsv
```

| Option | Default | Meaning |
| --- | --- | --- |
| `-m, --mode` | `xml` | output format (see below) |
| `-p, --path` | `scat-content/annotation/morphological` | source directory |
| `GLOB` (argument) | `*.tsv` | which files to read |

Output: `generated/converter/<mode>/<manuscript>.<mode>`.

**Output formats:**

- **`tsv`** — the source annotation columns with the computed lemma appended. The everyday tabular working format.
- **`xml`** — TEI P5, structured for import into [TXM](https://txm.gitpages.huma-num.fr/textometrie/) (XTZ profile). Each word is a `<w>` carrying its surface form, normalised form, morphological tag string, and lemma. The publication format.
- **`txt`** — plain running text in Church Slavonic Unicode (surface forms only).
- **`pkl`** — a `shelve` database mapping each normalised form to its attested analyses. Not an end product: it is the "precedent" store consumed by `annotator.py`. Unlike the other modes it is keyed by date and merges all input documents into one shelf.

### 3. `annotator.py` — semi-automatic morphological annotation

Given a tokenised text and a precedent shelf (from `converter.py -m pkl`), produces an Excel workbook that pre-fills unambiguous analyses and offers ambiguous ones as colour-coded dropdown lists, splitting the work across a number of annotators. Built for the department's annotation practicum.

```sh
# 1. build the precedent shelf from existing annotation
uv run python src/converter.py -m pkl        # -> generated/converter/pkl/<date>.pkl

# 2. tokenise the new manuscript
uv run python src/tokenizer.py "NewText.txt"  # -> generated/tokenizer/NewText.tsv

# 3. generate the workbook
uv run python src/annotator.py NewText.tsv <date>.pkl
```

| Argument / option | Default | Meaning |
| --- | --- | --- |
| `TEXT` | — | tokenised file, relative to `generated/tokenizer/` |
| `PICKLE` | — | precedent shelf, relative to `generated/converter/pkl/` |
| `--students` | `10` | number of annotators to split the work across |
| `--workload` | `250` | tokens per annotator sheet |
| `--offset` | `0` | skip this many leading lines |

Output: `generated/annotator/<text>.xlsx`.

## Development

Install the git hooks once:

```sh
uv run pre-commit install
```

Linting and formatting use [ruff](https://docs.astral.sh/ruff/); tests use [pytest](https://docs.pytest.org/):

```sh
uv run ruff check       # lint
uv run ruff format      # format
uv run pytest           # run the tests
uv run ty check src     # type-check (advisory, not enforced in CI)
```
