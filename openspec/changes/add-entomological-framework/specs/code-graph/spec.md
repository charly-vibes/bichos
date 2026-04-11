# Code Graph Specification

## ADDED Requirements

### Requirement: AST-Based Code Graph Construction
The system SHALL parse Python source files into a NetworkX DiGraph where functions and classes are nodes and call relationships are edges.

#### Scenario: Successful graph construction from Python repository
- **WHEN** `build_code_graph(root)` is called on a directory containing Python files
- **THEN** a `CodeGraph` is returned wrapping a `nx.DiGraph`
- **AND** every function, async function, and class definition appears as a node
- **AND** static call relationships appear as directed edges from caller to callee

#### Scenario: Node metadata includes required fields
- **WHEN** a function or class node is added to the graph
- **THEN** its `NodeMeta` MUST include: `name`, `qualified_name`, `file_path`, `lineno`, `loc`, and `complexity`
- **AND** `qualified_name` follows the pattern `module.path.function_name`
- **AND** `loc` is computed as `end_lineno - lineno + 1`

#### Scenario: Edge metadata includes call_count
- **WHEN** a call edge is added between two nodes
- **THEN** the edge MUST carry a `call_count` attribute initialized to 1
- **AND** `call_count` is incremented for each additional call site from the same caller

### Requirement: File Discovery and Filtering
The system SHALL discover Python files under a repository root while respecting ignore rules and configurable limits.

#### Scenario: .gitignore is respected
- **WHEN** a `.gitignore` file exists in the repository root
- **THEN** files matching its patterns SHALL be excluded from graph construction
- **AND** patterns are parsed using the `pathspec` library with gitignore syntax

#### Scenario: Always-excluded directories are filtered
- **WHEN** file discovery encounters `__pycache__` or `.git` directories
- **THEN** those directories SHALL be excluded regardless of `.gitignore` presence

#### Scenario: Fallback exclusions when no .gitignore
- **WHEN** no `.gitignore` file exists in the repository root
- **THEN** the system SHALL exclude common non-source directories: `.venv`, `venv`, `env`, `ENV`, `node_modules`, `dist`, `build`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.tox`, `site-packages`, `.eggs`

#### Scenario: max_files limit honored
- **WHEN** `build_code_graph(root, max_files=N)` is called
- **THEN** at most N Python files SHALL be processed
- **AND** files are selected in sorted order so results are deterministic

### Requirement: Cyclomatic Complexity Calculation
The system SHALL use radon to calculate per-function cyclomatic complexity and attach it to node metadata.

#### Scenario: Complexity calculated for each function
- **WHEN** a function node is registered in the graph
- **THEN** radon `cc_visit` SHALL be invoked on the source file
- **AND** the matching block's complexity value is stored in `NodeMeta.complexity`

#### Scenario: Default complexity of 1 for unparseable code
- **WHEN** radon fails to compute complexity for a function (parse error or no match)
- **THEN** the system SHALL assign a default complexity of 1

#### Scenario: Complexity cached in node metadata
- **WHEN** any consumer queries `CodeGraph.meta(qname).complexity`
- **THEN** the pre-computed complexity value is returned without re-invoking radon

### Requirement: Call Graph Extraction
The system SHALL perform static analysis of AST Call nodes to build call edges.

#### Scenario: Direct function calls detected
- **WHEN** a function body contains `foo()` (an `ast.Name` call)
- **THEN** an edge SHALL be created from the caller to the first node (in traversal order) whose simple name matches `foo`
- **NOTE** When multiple nodes share the same simple name, only the first match receives the edge. This is a known limitation of static name resolution.

#### Scenario: Attribute calls detected
- **WHEN** a function body contains `obj.bar()` (an `ast.Attribute` call)
- **THEN** an edge SHALL be created from the caller to the first node (in traversal order) whose simple name matches `bar`
- **NOTE** When multiple nodes share the same simple name, only the first match receives the edge. This is a known limitation of static name resolution.

#### Scenario: Multiple calls to same target increment call_count
- **WHEN** a function calls the same target function more than once
- **THEN** the edge `call_count` MUST be incremented for each additional call
- **AND** only one edge exists between the caller-callee pair

### Requirement: Graph Query API
The `CodeGraph` wrapper SHALL provide typed query methods for navigating and analyzing the graph.

#### Scenario: neighbors() returns callees
- **WHEN** `graph.neighbors(qname)` is called
- **THEN** a list of qualified names of direct callees is returned

#### Scenario: callers() returns callers
- **WHEN** `graph.callers(qname)` is called
- **THEN** a list of qualified names of nodes that call `qname` is returned

#### Scenario: nodes_by_complexity() returns ranked list
- **WHEN** `graph.nodes_by_complexity(top_n=N)` is called
- **THEN** a list of `(qualified_name, complexity)` tuples is returned
- **AND** the list is sorted by complexity descending
- **AND** at most N entries are returned

#### Scenario: nodes_in_file() filters by file
- **WHEN** `graph.nodes_in_file(rel_path)` is called
- **THEN** only nodes whose `file_path` matches `rel_path` are returned

#### Scenario: all_nodes() iterates all nodes
- **WHEN** `graph.all_nodes()` is called
- **THEN** an iterator of `(qualified_name, NodeMeta)` tuples is yielded for every node

#### Scenario: cycles() detects circular dependencies
- **WHEN** `graph.cycles()` is called
- **THEN** all simple cycles in the call graph are returned via `nx.simple_cycles`

#### Scenario: critical_nodes() ranks by betweenness centrality
- **WHEN** `graph.critical_nodes(top_n=N)` is called
- **THEN** nodes are ranked by betweenness centrality descending
- **AND** at most N entries are returned as `(qualified_name, centrality_score)` tuples

#### Scenario: heuristic_for() computes ACO heuristic η
- **WHEN** `graph.heuristic_for(qname)` is called on a known node
- **THEN** η = `complexity / max(1, loc)` is returned
- **AND** for unknown nodes, 1.0 is returned as default

### Requirement: Edge Case Handling
The system SHALL handle problematic inputs gracefully without crashing.

#### Scenario: Files with syntax errors are skipped
- **WHEN** a Python file contains syntax errors
- **THEN** the file SHALL be skipped during graph construction
- **AND** graph construction continues with remaining files

#### Scenario: Empty repositories produce empty graph
- **WHEN** the repository root contains no Python files
- **THEN** an empty `CodeGraph` with zero nodes and zero edges is returned

#### Scenario: Dynamic imports are not resolved
- **WHEN** code uses `importlib.import_module()` or similar dynamic import patterns
- **THEN** those imports SHALL NOT produce edges (known limitation of static analysis)

#### Scenario: eval/exec calls are not followed
- **WHEN** code contains `eval()` or `exec()` calls with dynamically constructed code
- **THEN** the system SHALL NOT attempt to analyze the generated code (known limitation)

#### Scenario: Files with encoding issues use replacement
- **WHEN** a Python file contains bytes not valid in UTF-8
- **THEN** the file SHALL be read with `errors="replace"` to avoid crashes

#### Scenario: C-extension modules are not parsed
- **WHEN** a module is implemented as a C extension (`.so`, `.pyd`)
- **THEN** the system SHALL only parse `.py` files (C extensions are excluded)

### Requirement: Performance Targets
The system SHALL meet defined performance targets for graph construction and querying.

#### Scenario: Graph construction for 10K LOC completes in < 5 seconds
- **WHEN** a repository with approximately 10,000 lines of Python code is analyzed
- **THEN** `build_code_graph()` SHALL complete in under 5 seconds on reference hardware

#### Scenario: Graph is read-only during agent execution
- **WHEN** agents (Ant, Termite, Hive) query the code graph concurrently
- **THEN** no write operations occur on the graph after construction
- **AND** no locking or synchronization is required for reads
