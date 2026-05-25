# Coding Standards

> *This specification uses terms defined in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).*
> *These standards are enforced by the SDD Harness. Violations are flagged
> during the `/review` phase.*

---

## 1. Language Rules (NON-NEGOTIABLE)

### 1.1. Source Code Language

All source code **MUST** be written in **English**. This includes:
- Variable names
- Function and method names
- Class and type names
- Enum values
- Constants
- Inline comments in source files
- Error messages in code

### 1.2. Documentation Language

Documentation files **MAY** be written in **English or Spanish**. Both languages
are equally valid. This applies to:
- Specifications (`specs/*.md`)
- Plans (`plans/*.md`)
- README files
- Decision log entries
- Commit messages
- Code review comments

> [!NOTE]
> Within a single document, one language **SHOULD** be used consistently.
> Mixing languages within a single document is discouraged but not prohibited.

---

## 2. Naming Conventions

### 2.1. Universal Rules

| Element | Convention | Example |
|---------|-----------|---------|
| Variables | `snake_case` | `sensor_value`, `max_retry_count` |
| Functions / Methods | `snake_case` | `read_sensor()`, `calculate_fft()` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_BUFFER_SIZE`, `DEFAULT_BAUD_RATE` |
| Classes / Types | `PascalCase` | `SensorDriver`, `DataProcessor` |
| Files | `snake_case` | `data_processor.py`, `sensor_driver.c` |
| Directories | `snake_case` | `test_utils/`, `data_models/` |
| Boolean variables | Prefix with verb | `is_ready`, `has_data`, `can_proceed` |

### 2.2. Naming Quality Rules

- **CS-01:** Names **MUST** be descriptive and self-documenting. Single-letter
  variables are only acceptable as loop counters (`i`, `j`, `k`) or in
  mathematical formulas where the letter has standard meaning (`x`, `y`, `n`).

- **CS-02:** Abbreviations **SHOULD** be avoided unless they are universally
  understood in the domain (e.g., `fft`, `gpio`, `uart`, `dma`, `pca`).

- **CS-03:** Names **MUST NOT** include the type (Hungarian notation is
  **PROHIBITED**). Use `count` not `int_count`, `name` not `str_name`.

---

## 3. Language-Specific Standards

### 3.1. Python

- **CS-PY-01:** Follow [PEP 8](https://peps.python.org/pep-0008/) for all
  formatting decisions not covered by this document.
- **CS-PY-02:** Use type hints for all function signatures.
  ```python
  def read_sensor(channel: int, timeout_ms: float = 100.0) -> float:
  ```
- **CS-PY-03:** Docstrings **MUST** use the Google docstring format.
  ```python
  def calculate_rms(data: list[float]) -> float:
      """Calculate the root mean square of a data array.

      Args:
          data: List of float values to process.

      Returns:
          The RMS value of the input data.

      Raises:
          ValueError: If data is empty.
      """
  ```
- **CS-PY-04:** Imports **MUST** be organized in three groups (standard library,
  third-party, local), separated by blank lines, and sorted alphabetically
  within each group.
- **CS-PY-05:** f-strings **SHOULD** be preferred over `.format()` or `%`
  string formatting.

### 3.2. C

- **CS-C-01:** Header files **MUST** use include guards with the pattern
  `#ifndef PROJECT_MODULE_H` / `#define PROJECT_MODULE_H`.
- **CS-C-02:** All functions **MUST** have a documentation comment above
  the declaration describing purpose, parameters, and return value.
  ```c
  /**
   * @brief Read a value from the specified ADC channel.
   *
   * @param channel ADC channel number (0-7).
   * @param timeout_ms Maximum wait time in milliseconds.
   * @return int Raw ADC value (0-4095), or -1 on timeout.
   */
  int read_adc_channel(uint8_t channel, uint32_t timeout_ms);
  ```
- **CS-C-03:** Curly braces **MUST** use the K&R style (opening brace on the
  same line as the statement).
  ```c
  if (condition) {
      // code
  } else {
      // code
  }
  ```
- **CS-C-04:** `#define` macros **MUST** use `UPPER_SNAKE_CASE` and be
  parenthesized to prevent operator precedence issues.
  ```c
  #define MAX_BUFFER_SIZE (1024)
  #define SQUARE(x) ((x) * (x))
  ```

### 3.3. VHDL

- **CS-VHDL-01:** Entity names **MUST** use `snake_case`.
- **CS-VHDL-02:** Signal names **MUST** use `snake_case` with descriptive
  prefixes where appropriate (e.g., `clk_`, `rst_`, `en_`).
- **CS-VHDL-03:** Constants **MUST** use `UPPER_SNAKE_CASE`.
- **CS-VHDL-04:** Each entity **MUST** have a header comment block describing
  its purpose, ports, and any timing constraints.
- **CS-VHDL-05:** Processes **MUST** have descriptive labels.
  ```vhdl
  counter_proc: process(clk, rst_n)
  begin
      -- process body
  end process counter_proc;
  ```

### 3.4. Verilog

- **CS-VER-01:** Module names **MUST** use `snake_case`.
- **CS-VER-02:** Wire and register names **MUST** use `snake_case`.
- **CS-VER-03:** Parameters **MUST** use `UPPER_SNAKE_CASE`.
- **CS-VER-04:** Always blocks **SHOULD** use `always_ff` and `always_comb`
  (SystemVerilog) when available.

### 3.5. LaTeX

- **CS-TEX-01:** Label names **MUST** use a prefix indicating the type:
  `fig:`, `tab:`, `eq:`, `sec:`, `ch:`, `lst:`.
  ```latex
  \label{fig:frequency_response}
  \label{eq:transfer_function}
  ```
- **CS-TEX-02:** Custom commands **MUST** use `PascalCase`.
- **CS-TEX-03:** File names **MUST** use `snake_case`.

### 3.6. MATLAB / Mathematica

- **CS-MAT-01:** Function names **MUST** use `snake_case` (MATLAB) or
  `PascalCase` (Mathematica, following Wolfram convention).
- **CS-MAT-02:** All scripts **MUST** begin with a header comment block
  describing purpose, inputs, outputs, and author.

---

## 4. Code Organization

### 4.1. File Structure

- **CS-10:** Each file **SHOULD** have a single, clear responsibility.
- **CS-11:** Files **MUST NOT** exceed 500 lines of code (excluding comments
  and blank lines). If a file exceeds this limit, it **SHOULD** be refactored
  into smaller modules.
- **CS-12:** Related files **MUST** be grouped in directories by feature or
  module, not by file type (e.g., `sensors/temperature.c` not
  `src/temperature.c` + `include/temperature.h` in separate trees — unless
  the project framework requires it).

### 4.2. Comments

- **CS-20:** Comments **MUST** explain **WHY**, not **WHAT**. The code itself
  should be self-documenting for the "what".
- **CS-21:** TODO comments **MUST** include a task reference:
  `// TODO(TASK-03): Implement retry logic`
- **CS-22:** Dead code (commented-out code blocks) **MUST NOT** be committed.
  Use version control to track historical code.

### 4.3. Formatting

- **CS-30:** Indentation **MUST** use spaces, not tabs.
  - Python: 4 spaces
  - C: 4 spaces
  - VHDL/Verilog: 4 spaces (or 2, consistently)
  - LaTeX: 2 spaces
- **CS-31:** Lines **SHOULD NOT** exceed 100 characters.
- **CS-32:** Files **MUST** end with a newline character.
