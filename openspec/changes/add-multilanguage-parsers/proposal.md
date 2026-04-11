# Change: Add Multi-Language Parsers (Go, JS, Rust, Clojure, Julia)

## Why

`build_code_graph` currently only parses Python source files via the built-in `ast`
module. As bichos is used to analyze polyglot repositories (and to dogfood itself on
non-Python codebases), the code graph must understand Go, JavaScript, Rust, Clojure,
and Julia in order for ant foragers and the ACO heuristic to function correctly. Without
multi-language support, all non-Python files are silently ignored, producing incomplete
call graphs and skewed complexity rankings.

## What Changes

- Introduce a `LanguageParser` Protocol in `src/bichos/graph/parsers/base.py` that
  defines the interface all language parsers must satisfy.
- Add five tree-sitter-backed parsers under `src/bichos/graph/parsers/`:
  - `go.py` — Go functions, methods, type/struct declarations, call expressions
  - `javascript.py` — JS/MJS function declarations, arrow functions, class declarations, call expressions
  - `rust.py` — Rust `fn`, `struct`, `enum`, `trait`, `impl` items, call and method-call expressions
  - `clojure.py` — Clojure `defn`/`defn-`/`fn`, `defprotocol`/`defrecord`, list-form invocations
  - `julia.py` — Julia function definitions, short-form functions, struct definitions, call expressions
- Extend `build_code_graph` (and the existing Python path) to dispatch on file
  extension, calling the appropriate parser and folding results into the same
  `CodeGraph`/`NodeMeta` structure.
- Add a `language: str` field to `NodeMeta` to track which parser produced each node.
- Add `tree-sitter` and five language-grammar packages to `pyproject.toml` dependencies.
- Complexity for non-Python nodes uses a branch-count heuristic (nesting depth of
  control-flow nodes) since `radon` is Python-only.

## Impact

- **Affected specs**: `code-graph-parsers` (new capability)
- **Affected code**:
  - `src/bichos/graph/models.py` — `NodeMeta` gains `language` field
  - `src/bichos/graph/builder.py` — dispatch logic, extension → parser map
  - `src/bichos/graph/parsers/` — new package (base protocol + 5 parsers)
  - `pyproject.toml` — new `tree-sitter*` dependencies
  - `tests/` — new fixture files and parser unit tests
- **No breaking changes** to public API: `build_code_graph(root, max_files)` signature
  unchanged; `NodeMeta` gains an optional field with a default.
- **No changes** to stigmergy, ACO math, or agent tools — they consume `CodeGraph`
  unchanged.
