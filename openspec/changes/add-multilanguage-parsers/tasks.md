## 1. Dependencies

- [ ] 1.1 Add `tree-sitter>=0.22,<1` to `[project.dependencies]` in `pyproject.toml`
- [ ] 1.2 Add `tree-sitter-go`, `tree-sitter-javascript`, `tree-sitter-rust`,
        `tree-sitter-clojure`, `tree-sitter-julia` to `[project.dependencies]`
- [ ] 1.3 Add `[[tool.mypy.overrides]]` stubs for all five grammar packages (none ship
        type stubs): `tree_sitter_go`, `tree_sitter_javascript`, `tree_sitter_rust`,
        `tree_sitter_clojure`, `tree_sitter_julia` — set `ignore_missing_imports = true`
        for each, matching the existing pattern for `radon.*` and `diskcache` in `pyproject.toml`
- [ ] 1.4 Run `uv sync` and verify `just check` passes on main branch before starting implementation

## 2. NodeMeta Extension

- [ ] 2.1 Add `language: str = "python"` field to `NodeMeta` in `src/bichos/graph/models.py`
- [ ] 2.2 Verify existing tests still pass (backward-compatible default)
- [ ] 2.3 Update `src/bichos/graph/builder.py` to pass `language="python"` explicitly
        when constructing `NodeMeta` (makes intent clear, no behavior change)

## 3. Parser Base Protocol

- [ ] 3.1 Create `src/bichos/graph/parsers/__init__.py` (empty, marks package)
- [ ] 3.2 Create `src/bichos/graph/parsers/base.py` with the following exact definitions:
  ```python
  from __future__ import annotations
  from pathlib import Path
  from typing import Protocol
  from bichos.graph.models import NodeMeta

  ParseResult = tuple[list[NodeMeta], list[tuple[str, str]]]
  # Second element: list of (caller_qualified_name, callee_simple_name) raw pairs.
  # Callee is always the simple name (e.g., "Bar", not "pkg.Bar").
  # build_code_graph resolves qualified callee via suffix-matching on registered nodes.

  class LanguageParser(Protocol):
      extensions: frozenset[str]
      def parse_file(self, path: Path, root: Path) -> ParseResult: ...
  ```
- [ ] 3.3 Confirm `uv run mypy src/bichos/graph/parsers/base.py` passes with zero errors

## 4. Python Parser (Refactor)

- [ ] 4.1 Create `src/bichos/graph/parsers/python.py` — move the helper functions
        `_extract_calls` and `_complexity_for` verbatim from `src/bichos/graph/builder.py`
        into this module (they become private helpers there). Implement `PythonParser`
        satisfying `LanguageParser`: `extensions = frozenset({".py"})`;
        `parse_file` does the same AST walk + radon pipeline as the current builder's
        first and second pass, but returns `(nodes, edges)` instead of mutating a graph.
        The caller qualified name format is unchanged:
        `module_name = rel_path.replace("/", ".").removesuffix(".py")`
        followed by `f"{module_name}.{node.name}"`.
- [ ] 4.2 After creating `parsers/python.py`, remove the now-duplicated `_extract_calls`,
        `_complexity_for`, and first/second-pass logic from `builder.py`; `builder.py`
        imports `PythonParser` via `_PARSERS` like all other parsers.
- [ ] 4.3 Write `tests/test_parsers_python.py`:
        - Call `PythonParser().parse_file(Path("tests/fixtures/simple_bugs/calculator.py"), root)`
        - Assert `nodes` contains a `NodeMeta` with `name="divide"`, `language="python"`, `loc >= 1`, `complexity >= 1`
        - Assert `nodes` contains a `NodeMeta` with `name="add"`, `language="python"`
        - Assert at least one edge tuple exists in the edges list
        - Call `parse_file` on a file with a syntax error (create an inline `tmp_path` fixture with `"def f(\n"`) and assert `([], [])` is returned
- [ ] 4.4 Run `uv run pytest tests/test_parsers_python.py -v` — all tests green

## 5. Go Parser

- [ ] 5.1 Create `src/bichos/graph/parsers/go.py` with `GoParser` satisfying `LanguageParser`
- [ ] 5.2 `extensions = frozenset({".go"})`
- [ ] 5.3 Initialise tree-sitter at module level with graceful degradation:
        ```python
        try:
            import tree_sitter_go as _ts_go
            from tree_sitter import Language, Parser as TSParser
            _GO_LANG = Language(_ts_go.language())
            _PARSER = TSParser(_GO_LANG)
            _AVAILABLE = True
        except ImportError:
            _AVAILABLE = False
        ```
        If `_AVAILABLE` is False, `parse_file` logs one warning via `loguru.logger` and
        returns `([], [])`.
- [ ] 5.4 Qualified name format: `module_name = str(path.relative_to(root)).replace("/", ".").removesuffix(".go")`; node qname = `f"{module_name}.{func_name}"`
- [ ] 5.5 Extract `function_declaration` and `method_declaration` → `NodeMeta(is_class=False, language="go")`
        For method declarations, the function name is the `name` child node's text.
- [ ] 5.6 Extract `type_declaration` that contains a `struct_type` or `interface_type` child → `NodeMeta(is_class=True, language="go")`
- [ ] 5.7 For each function/method body, walk descendants to collect `call_expression` nodes;
        extract the callee as the text of the `function` child (last dot-segment for selector
        expressions, e.g., `fmt.Println` → `"Println"`)
- [ ] 5.8 Complexity proxy: count descendant nodes of types `if_statement`, `for_statement`,
        `switch_statement`, `select_statement`, `case_clause`, `expression_case` in the
        function body + 1 (see design.md Decision 3 table)
- [ ] 5.9 Create `tests/fixtures/go_sample/sample.go`:
        ```go
        package main
        import "fmt"
        type Config struct { Debug bool }
        func NewConfig() Config { return Config{} }
        func (c Config) Validate() bool {
            if c.Debug { fmt.Println("debug") }
            return true
        }
        func Run() { cfg := NewConfig(); cfg.Validate() }
        ```
- [ ] 5.10 Write `tests/test_parsers_go.py`:
        - Assert nodes include `name="NewConfig"`, `name="Validate"`, `name="Run"`, `name="Config"`
        - Assert `Config` node has `is_class=True`
        - Assert edges include a tuple with callee `"NewConfig"` from `Run`'s qname
        - Assert `Validate`'s complexity == 2 (one `if_statement` + 1)
        - Assert syntax-error file returns `([], [])`
- [ ] 5.11 Run `uv run pytest tests/test_parsers_go.py -v`

## 6. JavaScript Parser

- [ ] 6.1 Create `src/bichos/graph/parsers/javascript.py` with `JavaScriptParser`
- [ ] 6.2 `extensions = frozenset({".js", ".mjs", ".cjs"})`
- [ ] 6.3 Same `_AVAILABLE` guard pattern as Go parser (task 5.3), using `tree_sitter_javascript`
- [ ] 6.4 Qualified name format: same as Go — path → dotted module name without extension
- [ ] 6.5 Function name resolution rules (in priority order):
        1. `function_declaration`: name = `name` child text
        2. `function_expression` or `arrow_function` inside a `variable_declarator`:
           name = the `name` child of the `variable_declarator`
        3. `method_definition` inside a `class_body`: name = `name` child text,
           scoped to the parent class name (e.g., `Animal.speak`)
        4. Unnamed functions (no declarator parent): **skip** — do not emit a node
- [ ] 6.6 Extract `class_declaration` → `NodeMeta(is_class=True, language="javascript")`;
        also extract each `method_definition` inside the class body as a separate node
        with `is_class=False` and name `ClassName.methodName`
- [ ] 6.7 Extract `call_expression` → raw edge callee = last identifier in the function
        child (e.g., `console.log` → `"log"`, `helper()` → `"helper"`)
- [ ] 6.8 Complexity proxy: count `if_statement`, `for_statement`, `for_in_statement`,
        `while_statement`, `switch_case`, `catch_clause`, `ternary_expression` + 1
        (drop `else_clause` — it does not add a new branch in McCabe terms)
- [ ] 6.9 Create `tests/fixtures/js_sample/sample.js`:
        ```js
        class Animal {
          constructor(name) { this.name = name; }
          speak() { if (this.name) { console.log(this.name); } }
        }
        function greet(animal) { animal.speak(); }
        const helper = () => { return greet(new Animal("cat")); };
        ```
- [ ] 6.10 Write `tests/test_parsers_javascript.py`:
        - Assert nodes include `name="Animal"` (`is_class=True`), `name="Animal.speak"`, `name="greet"`, `name="helper"`
        - Assert `Animal.speak` has complexity == 2 (one `if_statement` + 1)
        - Assert edges include callee `"speak"` from `greet`'s qname
        - Assert syntax-error file returns `([], [])`
- [ ] 6.11 Run `uv run pytest tests/test_parsers_javascript.py -v`

## 7. Rust Parser

- [ ] 7.1 Create `src/bichos/graph/parsers/rust.py` with `RustParser`
- [ ] 7.2 `extensions = frozenset({".rs"})`
- [ ] 7.3 Same `_AVAILABLE` guard pattern as Go parser (task 5.3), using `tree_sitter_rust`
- [ ] 7.4 Qualified name format: same path → dotted module derivation as other parsers;
        for methods inside `impl_item` blocks, suffix with `::method_name` relative to the
        impl's type name, e.g., qname = `f"{module_name}.Config__new"` (double-underscore
        because dots separate module segments, and `::` would break the suffix matcher).
        Use `Config__new` as the qualified segment, `new` as the simple name for edge lookup.
- [ ] 7.5 Extract top-level `function_item` → `NodeMeta(is_class=False, language="rust")`
- [ ] 7.6 Extract `struct_item`, `enum_item`, `trait_item` → `NodeMeta(is_class=True, language="rust")`
- [ ] 7.7 Extract `impl_item` blocks: for each `function_item` child, determine the impl type:
        - `impl Config { fn new() {} }` → type name = `Config`
        - `impl Trait for Config { fn method() {} }` → type name = `Config` (the "for" target)
        Both cases produce `NodeMeta(name="new", qualified_name=f"{module_name}.Config__new", is_class=False)`
- [ ] 7.8 Extract `call_expression` → callee = the `function` child text (last segment);
        extract `method_call_expression` → callee = the `name` child text
- [ ] 7.9 Complexity proxy: count `if_expression`, `match_expression`, `for_expression`,
        `while_expression`, `loop_expression`, and (if present in installed grammar version)
        `try_expression` nodes in the function body + 1
        (see design.md Decision 3 for the note on `try_expression` version variance)
- [ ] 7.10 Create `tests/fixtures/rust_sample/sample.rs`:
        ```rust
        struct Config { debug: bool }
        impl Config {
            fn new() -> Self { Config { debug: false } }
            fn validate(&self) -> bool {
                if self.debug { return false; }
                match self.debug { true => false, false => true }
            }
        }
        fn run() { let c = Config::new(); c.validate(); }
        ```
- [ ] 7.11 Write `tests/test_parsers_rust.py`:
        - Assert nodes include `name="Config"` (`is_class=True`), `name="new"`, `name="validate"`, `name="run"`
        - Assert `validate` has complexity == 3 (one `if_expression` + one `match_expression` + 1)
        - Assert edges include callee `"validate"` from `run`'s qname
        - Assert syntax-error file returns `([], [])`
- [ ] 7.12 Run `uv run pytest tests/test_parsers_rust.py -v`

## 8. Clojure Parser

- [ ] 8.1 Create `src/bichos/graph/parsers/clojure.py` with `ClojureParser`
- [ ] 8.2 `extensions = frozenset({".clj", ".cljs", ".cljc"})`
- [ ] 8.3 Same `_AVAILABLE` guard pattern as Go parser (task 5.3), using `tree_sitter_clojure`
- [ ] 8.4 Namespace / qualified name: Clojure files declare `(ns my.namespace ...)` as the first
        list form. Parse the `ns` symbol's second child text as the namespace string.
        If absent, fall back to the path-derived module name (same formula as other parsers).
        Node qname = `f"{namespace}.{fn_name}"`
- [ ] 8.5 Extract `defn` and `defn-` forms: walk the file's top-level list nodes; if the first
        child symbol is `"defn"` or `"defn-"`, the second child is the function name.
        Emit `NodeMeta(name=fn_name, is_class=False, language="clojure")`
- [ ] 8.6 Extract `defprotocol`, `defrecord`, `deftype` forms → `NodeMeta(is_class=True, language="clojure")`
- [ ] 8.7 Call extraction: within a function body (all children after the arg vector), collect
        list nodes whose first child is a symbol that appears in the set of names defined in
        this file (conservative — only intra-file calls are tracked; cross-namespace calls
        like `clojure.string/upper-case` produce no edge because the callee `upper-case`
        contains a hyphen and will not match any Python-qualified node in the graph).
- [ ] 8.8 Complexity proxy: count list-form first-child symbols matching `"if"`, `"when"`,
        `"cond"`, `"case"` within the function body + 1.
        Do NOT count `recur` — it is a tail-call, not a branch, and does not add cyclomatic
        complexity. Do NOT count `loop` — it is a binding form, not a conditional branch.
- [ ] 8.9 Create `tests/fixtures/clojure_sample/sample.clj`:
        ```clojure
        (ns myapp.core)
        (defn helper [x] (* x 2))
        (defn process [items]
          (if (empty? items)
            []
            (map helper items)))
        (defprotocol Printable (to-string [this]))
        ```
- [ ] 8.10 Write `tests/test_parsers_clojure.py`:
        - Assert nodes include `name="helper"` and `name="process"` (both `is_class=False, language="clojure"`)
        - Assert `name="Printable"` with `is_class=True`
        - Assert `process` has complexity == 2 (one `if` form + 1)
        - Assert edges include callee `"helper"` from `process`'s qname
        - Assert syntax-error file returns `([], [])`
- [ ] 8.11 Run `uv run pytest tests/test_parsers_clojure.py -v`

## 9. Julia Parser

- [ ] 9.1 Create `src/bichos/graph/parsers/julia.py` — begin with the module docstring:
        `"""Julia parser (experimental). Grammar coverage may be incomplete."""`
- [ ] 9.2 `extensions = frozenset({".jl"})`
- [ ] 9.3 Same `_AVAILABLE` guard pattern as Go parser (task 5.3), using `tree_sitter_julia`
- [ ] 9.4 Qualified name format: same path → dotted module derivation as other parsers
- [ ] 9.5 Extract `function_definition` nodes: name = child with field `name` → text
        Extract `short_function_definition` nodes (e.g., `square(x) = x*x`): name =
        the leftmost identifier in the left-hand side of the assignment
        Both → `NodeMeta(is_class=False, language="julia")`
- [ ] 9.6 Extract `struct_definition` → `NodeMeta(is_class=True, language="julia")`;
        name = the identifier child following the `struct` keyword
- [ ] 9.7 Extract `call_expression` → raw edge callee = the first child identifier text
        (e.g., `println(x)` → `"println"`, `Base.show(x)` → `"show"`)
- [ ] 9.8 Complexity proxy: count descendant nodes of types `if_statement`, `elseif_clause`,
        `for_statement`, `while_statement`, `try_statement` in the function body + 1
- [ ] 9.9 Create `tests/fixtures/julia_sample/sample.jl`:
        ```julia
        struct Point
            x::Float64
            y::Float64
        end
        function distance(a::Point, b::Point)
            dx = a.x - b.x
            dy = a.y - b.y
            if dx == 0 && dy == 0
                return 0.0
            end
            sqrt(dx^2 + dy^2)
        end
        magnitude(p::Point) = sqrt(p.x^2 + p.y^2)
        ```
- [ ] 9.10 Write `tests/test_parsers_julia.py`:
        - Skip all tests if `tree_sitter_julia` is not importable (`pytest.importorskip`)
        - Assert nodes include `name="Point"` (`is_class=True`), `name="distance"`, `name="magnitude"`
        - Assert `distance` has complexity == 2 (one `if_statement` + 1)
        - Assert edges include callee `"sqrt"` from `distance`'s qname
        - Assert syntax-error file returns `([], [])`
- [ ] 9.11 Run `uv run pytest tests/test_parsers_julia.py -v`

## 10. Builder Refactor

- [ ] 10.1 At the top of `src/bichos/graph/builder.py`, import all parsers and build the
        dispatch dict (using the shared-instance pattern from design.md Decision 5):
        ```python
        from bichos.graph.parsers.python import PythonParser
        from bichos.graph.parsers.go import GoParser
        # ... etc
        _py = PythonParser(); _go = GoParser(); _js = JavaScriptParser()
        _rs = RustParser(); _clj = ClojureParser(); _jl = JuliaParser()
        _PARSERS: dict[str, LanguageParser] = {
            ".py": _py, ".go": _go,
            ".js": _js, ".mjs": _js, ".cjs": _js,
            ".rs": _rs,
            ".clj": _clj, ".cljs": _clj, ".cljc": _clj,
            ".jl": _jl,
        }
        ```
- [ ] 10.2 Replace the existing two-filesystem-pass loop with a three-step in-memory structure:
        ```
        Step 1 — collect: for each file in sorted(root.rglob("*")) filtered to _PARSERS keys,
                 call parse_file() once, store (nodes, raw_edges) in a list.
                 Apply max_files cap BEFORE calling parse_file (slice the sorted file list).
        Step 2 — register: for each collected NodeMeta, call graph.add_node(qname, meta=meta)
        Step 3 — resolve:  for each (caller_qname, callee_name) in all collected raw_edges,
                 apply the existing suffix-matching logic unchanged:
                 for candidate in graph.nodes:
                     if candidate.endswith(f".{callee_name}"): add/increment edge; break
        ```
        This replaces the double file-read with a single-pass collect + in-memory resolve.
- [ ] 10.3 The `_extract_calls` and `_complexity_for` functions are now gone from `builder.py`
        (moved to `parsers/python.py` in task 4.1). Confirm `builder.py` no longer defines them.
- [ ] 10.4 Run `just check` (ruff + mypy + pytest) and fix any regressions before proceeding

## 11. Integration Test

- [ ] 11.1 Create `tests/fixtures/polyglot_sample/` with one file per supported language,
        each containing at least two functions with at least one call between them:
        - `main.py` — two Python functions, one calls the other
        - `util.go` — two Go functions, one calls the other
        - `helpers.js` — two JS functions, one calls the other
        - `lib.rs` — two Rust functions, one calls the other
        - `core.clj` — two Clojure defn forms, one calls the other
        - `ops.jl` — two Julia functions, one calls the other
        (These are independent per-language files; no cross-language calls are expected or tested.)
- [ ] 11.2 Write `tests/test_graph_polyglot.py`:
        ```python
        graph = build_code_graph(polyglot_sample_path)
        languages_present = {m.language for _, m in graph.all_nodes()}
        # At minimum Python, Go, JS, Rust, Clojure must be present
        # (Julia skipped if tree_sitter_julia not installed)
        assert "python" in languages_present
        assert "go" in languages_present
        assert "javascript" in languages_present
        assert "rust" in languages_present
        assert "clojure" in languages_present
        for _, meta in graph.all_nodes():
            assert meta.complexity >= 1
            assert meta.loc > 0
            assert meta.language in {"python","go","javascript","rust","clojure","julia"}
        assert graph.edge_count() >= 5  # at least one edge per language (minus optional Julia)
        ```
- [ ] 11.3 Run `just check` (ruff + mypy + pytest) — full suite must be green

## 12. Documentation

- [ ] 12.1 Update `openspec/project.md` to list `tree-sitter*` packages under Required dependencies
- [ ] 12.2 Add inline docstring to `build_code_graph` listing supported extensions
