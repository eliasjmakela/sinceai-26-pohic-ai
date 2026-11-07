# Third-party components

Every library, model, dataset, tool and service the submission uses, with its licence and commercial-use notes
(challenge brief §07). Rule: adding a dependency = adding a row here in the same commit (PRODUCT.md §8).
Part 1 (weighing) sources and packages: `part1/THIRD_PARTY_part1.md` (merged in when that branch lands).

## Data and starter kit
| Component | Version | Licence | Commercial-use note |
|---|---|---|---|
| Europress SMART Material Value Engine starter kit + synthetic dataset (Since AI / Europress) | 1.0.1 | **No licence file — terms to confirm with Since AI** | Synthetic data only; used under Since AI Hackathon 2026 rules; not redistributed in this repo |

## Python (pipeline)
| Component | Version | Licence | Commercial-use note |
|---|---|---|---|
| pandas | 3.1.1 | BSD-3-Clause | Permissive |
| numpy | 2.5.4 | BSD-3-Clause | Permissive |
| pyarrow | 26.0.1 | Apache-2.0 | Permissive |
| duckdb | 2.0.0 | MIT | Permissive |
| PyYAML | 6.0.3 | MIT | Permissive |
| pytz | 2026.6 | MIT | Permissive (kit dependency) |
| tabulate | 0.10.0 | MIT | Permissive (kit dependency) |
| scikit-learn | 1.9.1 | BSD-3-Clause | Permissive; used only to run the kit's ML baseline (B4) for the rules-vs-ML comparison |
| scipy | 1.18.1 | BSD-3-Clause | Permissive (scikit-learn dependency) |
| joblib | 1.6.0 | BSD-3-Clause | Permissive (scikit-learn dependency) |
| threadpoolctl | 3.8.0 | BSD-3-Clause | Permissive (scikit-learn dependency) |
| Markdown | 3.11.3 | BSD-3-Clause | Permissive (kit dev dependency) |
| pytest | 9.2.0 | MIT | Development only |
| ruff | 0.17.4 | MIT | Development only (lint) |

## Web (demo)
| Component | Version | Licence | Commercial-use note |
|---|---|---|---|
| React, React DOM | ^19.3.1 | MIT | Permissive |
| Recharts | ^3.10.1 | MIT | Permissive |
| Tailwind CSS, @tailwindcss/vite | ^4.3.5 | MIT | Permissive |
| Vite, @vitejs/plugin-react | ^8.3.6 / ^6.1.2 | MIT | Development / build only |
| TypeScript | ~7.0.2 | Apache-2.0 | Development / build only |
| oxlint | ^1.90.0 | MIT | Development only |
| @types/node, @types/react, @types/react-dom | see package.json | MIT | Development only |

## Tools and services
| Component | Licence / terms | Note |
|---|---|---|
| OpenAI Whisper (`large-v3-turbo`), run locally | MIT (code and weights) | Used to transcribe our own recordings of the Europress talks; not part of the product |
| Claude Code (Anthropic) | Anthropic commercial terms | Development tool (coding agents); not part of the product |
| Claude API (Anthropic) | Anthropic commercial terms | Only if the build-time AI customer brief (PRODUCT.md §7.6) is built |
