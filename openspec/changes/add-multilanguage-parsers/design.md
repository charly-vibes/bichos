# Design: Multi-Language Parser System

## Context

The code graph builder (`src/bichos/graph/builder.py`) is a two-pass Python-only AST
pipeline. Ant foragers navigate this graph using ACO, so the graph quality directly
affects bug detection coverage. Adding five languages requires:

1. A uniform parsing interface (Protocol) so `build_code_graph` stays simple.
2. A shared data contract (`NodeMeta`) that all parsers emit.
3. A complexity signal for non-Python code (radon works only on Python).
4. Minimal new dependencies that don't conflict with the no-infrastructure constraint.

## Goals / Non-Goals

- **Goals**:
  - Parse `.go`, `.js`/`.mjs`/`.cjs`, `.rs`, `.clj`/`.cljs`/`.cljc`, `.jl` files.
  - Produce `NodeMeta` nodes and directed call edges compatible with the existing `CodeGraph`.
  - Keep `build_code_graph` public API unchanged.
  - Maintain strict mypy and ruff compliance.
  - Unit-testable per parser (no full repo needed).

- **Non-Goals**:
  - Semantic type resolution (e.g., resolving which `foo` a call refers to across packages).
  - IDE-level cross-file name resolution for any language.
  - Support for TypeScript, JSX, or language dialects beyond vanilla JS.
  - Complexity metrics at par with radon's precision — a structural approximation suffices.

## Decisions

### Decision 1: tree-sitter as the unified parsing backend

**Chosen**: `tree-sitter>=0.22` with per-language grammar packages
(`tree-sitter-go`, `tree-sitter-javascript`, `tree-sitter-rust`,
`tree-sitter-clojure`, `tree-sitter-julia`).

**Rationale**:
- Single API surface for all five languages; incrementally adding more languages later
  costs one new package + one new file.
- Pure-Python bindings; no native build step at runtime beyond what pip installs.
- Grammar packages are maintained by the tree-sitter org and widely used (stable ABI).
- Supports structural queries (`Language.query(...)`) for extracting nodes by type.

**tree-sitter 0.22 API pattern** (breaking change from 0.21):
```python
# Grammar packages expose a .language() function returning a raw capsule.
# Wrap it with Language(), then pass to Parser().
import tree_sitter_go as ts_go
from tree_sitter import Language, Parser

GO_LANGUAGE = Language(ts_go.language())
_parser = Parser(GO_LANGUAGE)

# Parsing a file:
tree = _parser.parse(source_bytes)  # source must be bytes, not str
```
All five grammar packages follow the same pattern. Use `source.encode("utf-8")` before
passing to `_parser.parse()`.

**Alternatives considered**:
- *Language-specific tools per language* (gopls, esprima, rustc `--emit=ast`): each
  requires a separate subprocess, external toolchain install, and bespoke output parsing.
  Violates the no-external-infrastructure constraint and makes CI fragile.
- *Regex-based extraction*: fast but incorrect for nested definitions, string literals,
  and comments. Produces too many false nodes/edges to be useful.
- *pygments*: lexer-only, no parse tree — cannot extract call relationships.
- *libcst*: Python-only.

### Decision 2: `LanguageParser` as a structural Protocol (not ABC)

```python
class LanguageParser(Protocol):
    extensions: frozenset[str]
    def parse_file(self, path: Path, root: Path) -> tuple[list[NodeMeta], list[tuple[str, str]]]:
        ...
```

**Rationale**: Protocols allow duck typing — any object with the right shape satisfies
the contract. No inheritance required; parsers are simple module-level objects or small
classes. Compatible with mypy strict mode.

`parse_file` returns `(nodes, edges)` where:
- `nodes` is a list of `NodeMeta` (one per extracted function/class/struct).
- `edges` is a list of `(caller_qname, callee_name)` raw pairs that `build_code_graph`
  resolves in its existing second-pass suffix-matching logic.

### Decision 3: Complexity proxy for non-Python languages

`radon.complexity.cc_visit` parses Python bytecode and is not applicable to other
languages. For all non-Python parsers, complexity is approximated by **branch-node
count + 1**: count all control-flow nodes in a function body (if/else/for/while/switch/
match/case/select/cond/when/try/catch) and add 1. This mirrors the definition of
cyclomatic complexity (McCabe 1976) applied structurally.

The heuristic `η = complexity / max(1, loc)` used by the ACO engine does not depend
on radon's exact values — it only needs a positive integer that correlates with
code complexity. Branch-count satisfies this.

**Node types counted per language** (authoritative list; used in tasks and tests):

| Language | Counted node types |
|---|---|
| Go | `if_statement`, `for_statement`, `switch_statement`, `select_statement`, `case_clause`, `expression_case` |
| JavaScript | `if_statement`, `for_statement`, `for_in_statement`, `while_statement`, `switch_case`, `catch_clause`, `ternary_expression` |
| Rust | `if_expression`, `match_expression`, `for_expression`, `while_expression`, `loop_expression`, `try_expression` |
| Clojure | `if`, `when`, `cond`, `case` forms only — **not** `recur` (tail-call, not a branch) |
| Julia | `if_statement`, `elseif_clause`, `for_statement`, `while_statement`, `try_statement` |

Note on Rust `?` operator: in tree-sitter-rust ≥0.20, the `?` postfix is represented
as `try_expression` wrapping the inner expression. If `try_expression` is absent in
the installed version, the parser falls back to counting only the listed branch types
without it (a minor under-count, acceptable).

### Decision 4: `NodeMeta.language` field

Add `language: str = "python"` to `NodeMeta`. Default preserves backward compatibility
with existing Python nodes. Consumers (agents, tools, tests) that don't use `language`
are unaffected. The field enables language-specific analysis in future ant tool variants.

### Decision 5: Extension-to-parser dispatch in `build_code_graph`

Each parser instance is shared across all its extensions:

```python
_py  = PythonParser()
_go  = GoParser()
_js  = JavaScriptParser()
_rs  = RustParser()
_clj = ClojureParser()
_jl  = JuliaParser()

_PARSERS: dict[str, LanguageParser] = {
    ".py":   _py,
    ".go":   _go,
    ".js":   _js, ".mjs": _js, ".cjs": _js,
    ".rs":   _rs,
    ".clj":  _clj, ".cljs": _clj, ".cljc": _clj,
    ".jl":   _jl,
}
```

**Two-pass structure with protocol**: `parse_file` returns `(nodes, edges)` in one
call, but `build_code_graph` still needs all nodes registered before edges can be
resolved (suffix-matching requires the full node set). The updated pass structure is:

```
Pass 1 — collect:  call parse_file() for each file, store (nodes, raw_edges) per file
Pass 2 — register: add all collected NodeMeta to the graph
Pass 3 — resolve:  for each raw (caller_qname, callee_name), find matching node by suffix
```

This replaces the current two filesystem passes (which read each file twice). Files
are read once; the results are held in memory between passes. This is strictly better
than the old approach.

Files are collected with `sorted(root.rglob("*"))` filtered to registered extensions,
then sliced to `[:max_files]`. Sorting is alphabetical by full path (consistent with
the existing Python-only behavior). The `max_files` cap applies to the total count of
files across all languages, in sorted order.

### Decision 6: Packaging — `tree-sitter` in main dependencies, not optional

The parsers are a core capability (without them, multi-language repos silently produce
empty graphs). Placing `tree-sitter*` in `[project.dependencies]` ensures they are
always available. If a grammar package is unavailable at runtime, the parser logs a
warning and skips that file type (graceful degradation) rather than raising at import.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| tree-sitter ABI changes between grammar package versions | Pin `tree-sitter>=0.22,<1` and grammar packages to compatible minor versions |
| Grammar packages not available on all platforms | CI matrix includes linux/mac; graceful skip on import error |
| Clojure's LISP syntax makes call extraction ambiguous | Only extract list-form calls where the first element is a known `defn`-defined symbol; false negatives are acceptable |
| Clojure hyphenated names (e.g., `upper-case`) can't round-trip through suffix matching | The existing suffix matcher does `candidate.endswith(f".{call_name}")`. Hyphenated callee names will never match any Python-style qualified node. Accepted as false-negative for cross-namespace Clojure calls; intra-namespace calls still resolve correctly if the callee is defined in the same file. |
| Julia grammar package maturity | `tree-sitter-julia` is less mature; mark Julia parser as `experimental` in docstring; tests use simple fixtures |
| `max_files` cap applies to all files, reducing Python coverage in mixed repos | Document behavior; consider per-language caps in a future change |
| `max_files` ordering across languages | Files collected via `sorted(root.rglob("*"))` — alphabetical by full path. Deterministic; same as current Python-only behavior. |

## Open Questions

- Should `build_code_graph` accept a `languages: set[str] | None` filter to limit which
  parsers run? (Deferred — keep API minimal for now; can be added without breaking changes.)
- Should `.jsx`/`.tsx` be included? (Out of scope — vanilla JS only as specified.)
