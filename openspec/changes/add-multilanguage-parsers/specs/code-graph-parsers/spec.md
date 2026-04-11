# Code Graph Parsers Specification

## ADDED Requirements

### Requirement: Language Parser Protocol
The system SHALL define a `LanguageParser` Protocol that all language parsers MUST implement.

#### Scenario: Protocol enforces parse_file contract
- **WHEN** a class implements `LanguageParser`
- **THEN** it MUST expose `extensions: frozenset[str]` listing the file suffixes it handles
- **AND** it MUST implement `parse_file(path: Path, root: Path) -> tuple[list[NodeMeta], list[tuple[str, str]]]`
- **AND** mypy strict mode MUST accept it as a valid `LanguageParser` at all call sites

#### Scenario: parse_file returns nodes and raw edges
- **WHEN** `parse_file` is called on a source file
- **THEN** it returns a list of `NodeMeta` (one per extracted definition)
- **AND** a list of `(caller_qualified_name, callee_name)` raw edge pairs
- **AND** edges use the simple function name (not qualified) for the callee, matching the existing suffix-resolution logic in `build_code_graph`

#### Scenario: Parse errors are handled gracefully
- **WHEN** a source file has a syntax error
- **THEN** `parse_file` returns `([], [])` and logs a warning via Loguru
- **AND** does NOT raise an exception
- **AND** `build_code_graph` continues processing remaining files

---

### Requirement: NodeMeta Language Field
`NodeMeta` SHALL carry a `language` field identifying which parser produced the node.

#### Scenario: Python nodes retain correct language
- **WHEN** the Python parser processes a `.py` file
- **THEN** all resulting `NodeMeta` instances have `language == "python"`

#### Scenario: Non-Python nodes carry language tag
- **WHEN** a non-Python parser processes a source file
- **THEN** all resulting `NodeMeta` instances carry the correct language tag
  (e.g., `"go"`, `"javascript"`, `"rust"`, `"clojure"`, `"julia"`)

#### Scenario: Backward compatibility — default language is python
- **WHEN** a `NodeMeta` is constructed without specifying `language`
- **THEN** `language` defaults to `"python"`
- **AND** existing code that constructs `NodeMeta` without `language` continues to work

---

### Requirement: Extension-Based Parser Dispatch
`build_code_graph` SHALL automatically dispatch to the correct parser based on file extension.

#### Scenario: All registered extensions are processed
- **WHEN** `build_code_graph` is called on a directory containing `.go`, `.js`, `.rs`, `.clj`, and `.jl` files
- **THEN** each file is routed to its corresponding language parser
- **AND** nodes from all languages appear in the returned `CodeGraph`

#### Scenario: Unknown extensions are silently skipped
- **WHEN** `build_code_graph` encounters a file with extension `.html`, `.md`, or `.txt`
- **THEN** the file is ignored without error or warning
- **AND** the graph is not affected

#### Scenario: max_files cap applies across all languages
- **WHEN** `build_code_graph(root, max_files=10)` is called on a repo with 20 files across languages
- **THEN** at most 10 files are parsed in total
- **AND** the `max_files` limit is documented as applying globally

---

### Requirement: Qualified Name Format
All language parsers SHALL produce qualified node names using a uniform dotted-path format derived from the source file's relative path.

#### Scenario: Qualified name derived from file path
- **WHEN** a file at `src/utils/helpers.go` is parsed relative to repo root
- **THEN** the module prefix is `src.utils.helpers` (slashes replaced with dots, extension stripped)
- **AND** a function `Foo` in that file has `qualified_name == "src.utils.helpers.Foo"`
- **AND** this applies to all language parsers (Python, Go, JavaScript, Rust, Clojure, Julia)

#### Scenario: Rust impl methods use double-underscore scoping
- **WHEN** a Rust `impl Config` block contains `fn new()`
- **THEN** the qualified name is `module.Config__new` (type and method joined with `__`)
- **AND** the simple `name` field on `NodeMeta` is `"new"`
- **AND** the suffix-matcher in `build_code_graph` resolves callee `"new"` against this node correctly

#### Scenario: Clojure uses ns-declared namespace as prefix
- **WHEN** a Clojure file declares `(ns myapp.core)` and defines `(defn greet [])`
- **THEN** the qualified name is `"myapp.core.greet"`
- **WHEN** no `ns` declaration is present
- **THEN** the path-derived module name is used as the prefix instead

---

### Requirement: Go Parser
The system SHALL parse Go source files (`.go`) and extract definitions and call relationships.

#### Scenario: Extract top-level and method functions
- **WHEN** a `.go` file contains `func Foo() {}` and `func (r *Receiver) Bar() {}`
- **THEN** two `NodeMeta` nodes are produced with `name="Foo"` and `name="Bar"`
- **AND** `language == "go"` on both nodes
- **AND** `is_class == False` for function nodes

#### Scenario: Extract type/struct declarations
- **WHEN** a `.go` file contains `type Point struct { X, Y float64 }`
- **THEN** a `NodeMeta` node is produced with `name="Point"` and `is_class == True`

#### Scenario: Extract call expressions
- **WHEN** function `Foo` calls `Bar()` and `fmt.Println()`
- **THEN** edges `("pkg.Foo", "Bar")` and `("pkg.Foo", "Println")` are included in raw edges
- **AND** the qualified callee is resolved later by `build_code_graph`'s suffix-matching logic

#### Scenario: Go complexity proxy
- **WHEN** a Go function contains `if`, `for`, `switch`, and `select` statements
- **THEN** `NodeMeta.complexity` equals the count of branch nodes + 1
- **AND** `complexity >= 1` for all nodes

---

### Requirement: JavaScript Parser
The system SHALL parse vanilla JavaScript source files (`.js`, `.mjs`, `.cjs`) and extract definitions and call relationships.

#### Scenario: Extract function declarations and expressions
- **WHEN** a `.js` file contains `function greet() {}`, `const fn = function() {}`, and `const arrowFn = () => {}`
- **THEN** three `NodeMeta` nodes are produced with `name="greet"`, `name="fn"`, `name="arrowFn"` (variable name used for expressions and arrow functions)
- **AND** `language == "javascript"` on all nodes

#### Scenario: Anonymous functions without declarators are skipped
- **WHEN** a `.js` file contains an immediately-invoked function expression such as `(function() {})()`
- **THEN** no `NodeMeta` node is produced for that expression
- **AND** `build_code_graph` continues without error

#### Scenario: Extract class declarations
- **WHEN** a `.js` file contains `class Animal { constructor() {} speak() {} }`
- **THEN** a `NodeMeta` node is produced with `name="Animal"` and `is_class == True`
- **AND** `constructor` and `speak` are also extracted as function nodes

#### Scenario: Extract call expressions
- **WHEN** function `greet` calls `console.log()` and `helper()`
- **THEN** raw edges include `("module.greet", "log")` and `("module.greet", "helper")`

#### Scenario: JavaScript complexity proxy
- **WHEN** a JS function contains `if`, `else if`, `for`, `while`, `switch`, `case`, `catch`, and ternary `?` expressions
- **THEN** `NodeMeta.complexity` equals the count of those control-flow nodes + 1

---

### Requirement: Rust Parser
The system SHALL parse Rust source files (`.rs`) and extract definitions and call relationships.

#### Scenario: Extract function items
- **WHEN** a `.rs` file contains `fn process(input: &str) -> Result<(), Error> {}`
- **THEN** a `NodeMeta` node is produced with `name="process"` and `is_class == False`
- **AND** `language == "rust"`

#### Scenario: Extract struct, enum, and trait items
- **WHEN** a `.rs` file contains `struct Config {}`, `enum Status {}`, and `trait Runnable {}`
- **THEN** three `NodeMeta` nodes are produced with `is_class == True`

#### Scenario: Extract impl blocks as method containers (inherent impl)
- **WHEN** a `.rs` file contains `impl Config { fn new() -> Self {} fn validate(&self) {} }`
- **THEN** `new` and `validate` are extracted as function nodes scoped to `Config`
- **AND** their qualified names include the impl type using double-underscore notation (e.g., `module.Config__new`)

#### Scenario: Extract trait impl blocks
- **WHEN** a `.rs` file contains `impl Runnable for Config { fn run(&self) {} }`
- **THEN** `run` is extracted as a function node scoped to `Config` (the "for" target, not the trait)
- **AND** its qualified name follows the same `Config__run` pattern as inherent impl methods

#### Scenario: Extract call and method-call expressions
- **WHEN** function `run` calls `process(data)` and `config.validate()`
- **THEN** raw edges include `("module.run", "process")` and `("module.run", "validate")`

#### Scenario: Rust complexity proxy
- **WHEN** a Rust function contains `if`, `match`, `for`, `while`, `loop`, and `?` try expressions
- **THEN** `NodeMeta.complexity` equals the count of those nodes + 1

---

### Requirement: Clojure Parser
The system SHALL parse Clojure source files (`.clj`, `.cljs`, `.cljc`) and extract definitions and call relationships.

#### Scenario: Extract defn and defn- definitions
- **WHEN** a `.clj` file contains `(defn greet [name] ...)` and `(defn- helper [] ...)`
- **THEN** two `NodeMeta` nodes are produced with `name="greet"` and `name="helper"`
- **AND** `language == "clojure"` and `is_class == False`

#### Scenario: Extract defprotocol and defrecord as type nodes
- **WHEN** a `.clj` file contains `(defprotocol Printable ...)` and `(defrecord Point [x y] ...)`
- **THEN** two `NodeMeta` nodes are produced with `is_class == True`

#### Scenario: Extract intra-file function call relationships
- **WHEN** `greet` calls `helper` (defined in the same file)
- **THEN** raw edges include `("ns.greet", "helper")`

#### Scenario: Cross-namespace calls with hyphens produce no edge
- **WHEN** `greet` calls `clojure.string/upper-case`
- **THEN** no edge is emitted for `upper-case`
- **AND** this is accepted as a false negative — hyphenated names cannot be resolved by the suffix-matcher and are silently dropped

#### Scenario: Clojure complexity proxy
- **WHEN** a Clojure function body contains `if`, `when`, `cond`, and `case` forms
- **THEN** `NodeMeta.complexity` equals the count of those forms + 1
- **AND** `recur` and `loop` forms are NOT counted (tail-call and binding form respectively, not branches)

---

### Requirement: Julia Parser
The system SHALL parse Julia source files (`.jl`) and extract definitions and call relationships.

#### Scenario: Extract function definitions
- **WHEN** a `.jl` file contains `function greet(name::String) ... end` and `square(x) = x * x`
- **THEN** two `NodeMeta` nodes are produced with `name="greet"` and `name="square"`
- **AND** `language == "julia"` and `is_class == False`

#### Scenario: Extract struct definitions
- **WHEN** a `.jl` file contains `struct Point x::Float64; y::Float64 end`
- **THEN** a `NodeMeta` node is produced with `name="Point"` and `is_class == True`

#### Scenario: Extract call expressions
- **WHEN** `greet` calls `println(name)` and `process(data)`
- **THEN** raw edges include `("module.greet", "println")` and `("module.greet", "process")`

#### Scenario: Julia complexity proxy
- **WHEN** a Julia function contains `if`, `elseif`, `for`, `while`, and `try` blocks
- **THEN** `NodeMeta.complexity` equals the count of those nodes + 1

---

### Requirement: Graceful Degradation on Missing Grammar Package
The system SHALL continue functioning if a language grammar package is not installed.

#### Scenario: Missing grammar package skips language silently
- **WHEN** `tree-sitter-julia` is not installed
- **THEN** `.jl` files are skipped with a single logged warning at startup
- **AND** Python, Go, JS, Rust, and Clojure files are still parsed normally
- **AND** `build_code_graph` does NOT raise an `ImportError`

---

### Requirement: Parser Unit Tests
Each language parser SHALL have dedicated unit tests using small fixture files.

#### Scenario: Each parser test covers node extraction
- **WHEN** `parse_file` is called on a fixture file for a given language
- **THEN** the expected `NodeMeta` nodes are returned with correct `name`, `language`, `loc`, `complexity`

#### Scenario: Each parser test covers edge extraction
- **WHEN** `parse_file` is called on a fixture file containing known function calls
- **THEN** the expected raw edges are present in the returned edge list

#### Scenario: Each parser test verifies syntax error resilience
- **WHEN** `parse_file` is called on an intentionally malformed source file
- **THEN** an empty result `([], [])` is returned without raising
