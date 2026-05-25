# Security Rules

> *This specification uses terms defined in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).*
> *The active security profile is determined by `harness-config.yaml` → `harness.security_profile`.*

---

## General Rules (All Profiles)

These rules apply regardless of the selected security profile.

### Secrets and Credentials

- **R-001:** The agent **MUST NOT** generate, store, or hardcode any API keys,
  tokens, passwords, certificates, or other secrets in source code, configuration
  files, or documentation. All sensitive values **MUST** be read from environment
  variables, secure vaults, or configuration files excluded from version control.

- **R-002:** Files containing secrets (e.g., `.env`, `credentials.json`) **MUST**
  be listed in `.gitignore` before any commit. The agent **MUST** verify this.

- **R-003:** The agent **MUST NOT** log, print, or display secret values in any
  output, even for debugging purposes.

### Input Validation

- **R-010:** All external inputs **MUST** be validated before processing.
  "External" means any data that crosses a trust boundary: user input, network
  data, sensor readings, file contents, serial communication.

- **R-011:** The agent **MUST NOT** assume input data is well-formed. All parsing
  routines **MUST** handle malformed, truncated, or unexpected data gracefully.

### Error Handling

- **R-020:** In production/release builds, the application **MUST NOT** expose
  internal error details (stack traces, memory addresses, file paths) to
  external interfaces. Errors **MUST** be logged internally and a generic
  error response provided externally.

---

## Profile: `embedded` (Default)

_Applies to firmware, microcontroller, and FPGA projects._

### Memory Safety

- **R-100:** All dynamically allocated memory **MUST** be explicitly freed.
  The agent **SHOULD** prefer stack allocation over heap allocation where
  possible.

- **R-101:** All buffer operations **MUST** include bounds checking. Functions
  like `strcpy`, `sprintf`, and `gets` **MUST NOT** be used. Use their
  bounded alternatives (`strncpy`, `snprintf`, `fgets`).

- **R-102:** Array indices **MUST** be validated against array bounds before
  access. Out-of-bounds access **MUST** be treated as a critical error.

### Communication Security

- **R-110:** All data received via serial (UART), I2C, SPI, or any other
  communication bus **MUST** be validated before processing. This includes
  checking packet headers, lengths, and checksums.

- **R-111:** The agent **MUST NOT** assume a fixed packet size unless the
  protocol specification explicitly guarantees it. Variable-length protocols
  **MUST** include length fields and validate them.

- **R-112:** DMA buffers and interrupt-shared variables **MUST** be declared
  with appropriate volatile qualifiers and protected with synchronization
  primitives (mutexes, critical sections).

### Firmware-Specific

- **R-120:** Watchdog timers **SHOULD** be configured in production firmware
  to recover from unexpected hangs.

- **R-121:** Flash/EEPROM write operations **MUST** include verification
  (read-back) to ensure data integrity.

- **R-122:** Unused GPIO pins **SHOULD** be configured as inputs with pull-down
  resistors to prevent floating states.

---

## Profile: `data-science`

_Applies to data analysis, machine learning, and AI projects._

### Data Privacy

- **R-200:** Personally Identifiable Information (PII) **MUST NOT** be included
  in committed notebooks, scripts, or output files. Datasets containing PII
  **MUST** be excluded from version control.

- **R-201:** The agent **MUST NOT** display raw sensitive data in notebook
  outputs or logs. Sample data **SHOULD** be anonymized or use synthetic
  examples.

- **R-202:** Dataset file paths **MUST** use relative paths or environment
  variables to maintain portability and avoid exposing local directory structures.

### Reproducibility

- **R-210:** All random operations (random seeds, train/test splits, model
  initialization) **MUST** use explicit, documented seeds for reproducibility.

- **R-211:** Dependency versions **MUST** be pinned (e.g., `requirements.txt`
  with exact versions or `poetry.lock`).

### API and External Services

- **R-220:** API keys for external services (OpenAI, HuggingFace, cloud
  providers) **MUST** be loaded from environment variables, never hardcoded.

- **R-221:** Rate limiting and retry logic **SHOULD** be implemented for all
  external API calls to prevent accidental excessive usage.

---

## Profile: `web`

_Applies to web APIs, web applications, and backend services._

### Authentication and Authorization

- **R-300:** The application **MUST** use OAuth 2.0 with PKCE for all user
  authentication flows.

- **R-301:** Session tokens **MUST** have configurable expiration times and
  **MUST** be invalidated on logout.

- **R-302:** All endpoints that access or modify user data **MUST** verify
  authorization before processing the request.

### Database Security

- **R-310:** All database queries **MUST** use parameterized queries or ORM
  methods that prevent SQL injection. Raw string concatenation for queries
  is **PROHIBITED**.

- **R-311:** Database connection strings **MUST** be loaded from environment
  variables, not hardcoded.

### API Security

- **R-320:** All API endpoints **MUST** validate request body schemas and
  reject malformed requests with appropriate HTTP status codes (400, 422).

- **R-321:** CORS (Cross-Origin Resource Sharing) **MUST** be explicitly
  configured. The wildcard origin (`*`) **MUST NOT** be used in production.

- **R-322:** Rate limiting **MUST** be implemented on authentication endpoints
  to prevent brute-force attacks.

---

## Profile: `custom`

_When `security_profile` is set to `"custom"`, only the General Rules (R-001
through R-020) apply by default. Add project-specific rules below._

### Custom Rules

- **R-900:** [Add your custom security rules here]
