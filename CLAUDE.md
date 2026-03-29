# CLAUDE.md

## After making changes

Always run `pre-commit run --all-files` after making any code changes and fix any issues before finishing.

## Personal values

Never commit personal values to the codebase — no real names, email addresses, home addresses, phone numbers, or any other personally identifiable information. Use generic placeholders instead (e.g. `user`, `partner`, `home`, `home_uk`).

---

## Code conventions

### Type annotations
- Every function parameter and return type is annotated, including `__init__` (`-> None`)
- Use `T | None` rather than `Optional[T]`
- Use `X | Y` rather than `Union[X, Y]`
- Use built-in generics: `list[T]`, `dict[K, V]`, `tuple[T, ...]`, `type[T]` — never `List`, `Dict`, `Tuple`, `Type` from `typing`
- `Sequence` and `Iterable` come from `collections.abc`, not `typing`
- Keep `Any` and `cast` from `typing`
- Do not annotate local variables

### Pydantic models
- Inherit from `BaseModel` for all data models
- Declare field defaults with `Field()`: `location: Optional[str] = Field(None)`, `description: str = Field("")`
- Use `@model_validator(mode="before")` for construction-time transformation
- Serialise with `model_dump(mode="json")` and deserialise with `model_validate()`
- Prefer `@classmethod` factory methods named `from_<source>` (e.g. `from_dict`, `from_key`, `from_result`)

### Class structure
Order members as follows:
1. Class-level attributes / Pydantic fields
2. `__init__`, `__str__`, other dunder methods
3. `@property` methods
4. `@classmethod` methods
5. `@staticmethod` methods

### Imports
- Three groups, separated by blank lines: stdlib → third-party → local (`src.*`)
- Alphabetically sorted within each group (enforced by isort)
- Use absolute imports throughout (`from src.models.calendar import ...`)

### `__all__` and package exports
- `__all__` belongs exclusively in `__init__.py` files — never in regular modules
- Every `__init__.py` under `src/` must declare `__all__` and re-export the public symbols of its direct modules
- Format: `__all__` list first (alphabetically sorted), then the corresponding imports, e.g.:
  ```python
  __all__ = [
      "LocationCategory",
      "TransportMode",
  ]

  from .location_category import LocationCategory
  from .transport_mode import TransportMode
  ```
- For packages with sub-packages, each level maintains its own `__init__.py`; deeper levels may also group exports
- Exception: `src/__init__.py` is intentionally left empty — `address_parser` sits at the base of the dependency tree and eagerly importing it from the top-level package creates a circular import

### Error handling
- Raise specific built-in exceptions with descriptive f-string messages:
  `raise ValueError(f"Key '{key}' not in original dictionary")`
- Use `TypeError` for type mismatches, `ValueError` for invalid values
- Let exceptions propagate unless there is a specific recovery action (e.g. rate-limit retry)
- Catch narrow exception types, never bare `except:`

### Logging
- Use stdlib `logging` throughout
- Every module gets a named logger: `logger = logging.getLogger(__name__)` (placed after imports)
- All logging calls use the module-level `logger` object, never `logging.info()` directly
- Use `Formatter` helpers for structured output: `logger.info(Formatter.title("Loading"))`
- Use f-strings for dynamic content: `logger.info(f"Processing {name}")`
- Pass `extra={"markup": True}` when using Rich markup in messages

### File I/O
- All paths as `pathlib.Path`, never bare strings
- Use the `File` utility class for all reads/writes (`File.read_json`, `File.write_csv`, etc.)
- Always specify `encoding="utf-8"` explicitly
- Indent JSON output with tabs: `json.dump(..., indent="\t")`

### Naming
- Classes: `PascalCase`
- Functions, methods, variables: `snake_case`
- Enum members: `SCREAMING_SNAKE_CASE` (`Owner.USER`, `Owner.SHARED`, `LocationCategory.RESTAURANT`)
- No private `_method` prefix convention

### Enums
- All enums use `auto()` for values — no explicit string or integer values
- Add a `from_str(cls, value: str)` classmethod to each enum that deserializes strings: `cls[value.upper()]`
- In Pydantic models that use enums, add `@field_validator(mode="before")` to convert strings to enum members
- Field validators must handle both string and integer inputs (integers for backward compatibility with older serializations):
  ```python
  @field_validator("category", mode="before")
  @classmethod
  def parse_category(cls, value: str | LocationCategory | int) -> LocationCategory:
      if isinstance(value, LocationCategory):
          return value
      if isinstance(value, str):
          return LocationCategory.from_str(value)
      if isinstance(value, int):
          for member in LocationCategory:
              if member.value == value:
                  return member
          raise ValueError(f"No LocationCategory enum member with value {value}")
  ```
- Serialization of enums to dict/JSON: use `enum_member.name.lower()` to get the string representation

### Strings
- f-strings exclusively — no `.format()`, no concatenation for non-trivial strings

### Collections
- Prefer list/dict comprehensions over explicit loops where readable
- Use `defaultdict` for accumulation patterns
- Subclass `List[T]` for domain collections with behaviour (e.g. `class Activities(List[Activity])`)
- Lambda functions for sort keys

### Scripts
- All scripts inherit from the `Script` ABC and implement `run()`
- Intermediate base classes (`ActivityScript`, `MediaScript`, `LocationScript`) hold shared setup logic
- Shared user-input helpers live on the base class (`get_owner()`, `get_location()`)

### Linting / formatting
- Line length: 120 characters
- Formatter: Black
- Import sorter: isort (Black-compatible profile)
- Type checker: mypy in strict mode (`disallow_untyped_defs`, `strict_optional`, `no_implicit_optional`)
- Flake8 with complexity limits: max expression complexity 12, max cognitive complexity 17
