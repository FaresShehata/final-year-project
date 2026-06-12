"""
Type hints as described here are a subset of the full Python 3.8 specification.
See https://docs.python.org/3/library/typing.html#module-contents ."""

from typing import *
import sys
from collections.abc import Iterable
from functools import partial
from inspect import signature
from itertools import chain, repeat
from operator import itemgetter
from random import randint
import re
import time
from types import UnionType
from warnings import warn as warning

if sys.version_info >= (3,9):
    from collections.abc import Callable as Callable_T
else:
    from typing_extensions import Literal as Literal_T
    from typing_extensions import Protocol as Protocol_T
    from typing_extensions import TypedDict as TypedDict_T
    from typing_extensions import TypeAlias as TypeAlias_T
    from typing_extensions import Concatenate as Concatenate_T
    from typing_extensions import ParamSpec as ParamSpec_T
    from typing_extensions import Self as Self_T
    from typing_extensions import ForwardRef as ForwardRef_T
    from typing_extensions import NotRequired as NotRequired_T

    class Protocol_T(Protocol): pass
    class TypedDict_T(TypedDict): pass
    class ForwardRef_T(FutureWarning): pass
    class NotRequired_T(DeprecationWarning): pass
    class Concatenate_T(DeprecationWarning): pass
    class ParamSpec_T(DeprecationWarning): pass
    class Self_T(DeprecationWarning): pass

from unicodedata import (
    category,
    normalize,
)

from rich.console import ConsoleRenderable
from rich.text import Text
from rich.style import StyleType as RichStyleType
from rich.repr import rich_repr
from rich.segment import Segment as RichSegment

from pydantic import (
    BaseModel,
    StrictStr as StrictStr_T,
    constr,
    validator,
    before_validator,
)
from pydantic.fields import FieldInfo, ModelField
from pydantic.json_schema import JsonSchemaValue
from pydantic.utils import is_class_var_defined
from pydantic.typing import get_origin, get_args, get_type_hints

from ..util._compat import (
    ClassVar,
    Deque,
    ExtensionModule,
    List,
    Optional,
    Set,
    Tuple,
    Dict,
    FrozenSet,
    Generic,
    Sequence,
    MutableSequence,
    Mapping,
    MutableMapping,
    ByteString,
    AnyStr,
    SupportsIndex,
    Hashable,
    BaseExceptionGroup,
    Any,
    Coroutine,
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    Generator,
    Iterator,
    Reversible,
    Sized,
    Container,
    MutableSet,
    MutableMappingView,
    MutableMappingItemsView,
    MutableMappingKeysView,
    MutableMappingValuesView,
    TypeGuard,
    cast,
    overload,
    override,
    assert_never,
    is_typeddict,
    get_origin,
    get_args,
    get_type_hints,
    get_type_hints_from_call,
    get_annotations,
    get_args_from_call,
    get_field_annotation,
    get_fields,
    get_validators_for_model,
    get_attrs_for_model,
    model_copy,
    model_validate,
    model_validate_raw,
    model_dump,
    model_dump_json,
    model_parse,
    model_parse_raw,
    model_preparse,
    model_rebuild,
    model_rerun_validators,
    model_asdict,
    model_issubclass,
    model_isinstance,
    model_to_asyngenerator,
    model_to_awaitable,
    model_to_asyncgenerator,
    model_to_coroutine,
    model_to_deque,
    model_to_dict,
    model_to_frozenset,
    model_to_generator,
    model_to_iterator,
    model_to_list,
    model_to_mutablemappingview,
    model_to_mutableset,
    model_to_mutablesequence,
    model_to_set,
    model_to_sequence,
    model_to_tuple,
    model_to_typemapping,
    model_to_union,
    model_to_valuesview,
    model    return isinstance(x, str) and len(x) <= 20


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
    label:   Annotated[str,   short_str] = _Constrained()  # type: ignore[assignment]

    def __init__(self, label: str, reading: float):
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
        return max(0, min(self.end, other.end) - max(self.start, other.start))


# ── numbers ABC ──────────────────────────────────────────────────────────────

class Rational(numbers.Rational):
    """Minimal rational backed by integer numerator/denominator."""

    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError
