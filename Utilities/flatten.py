"""
This helper module provides functions for flattening Speckle object trees and
extracting base objects along with their transformations. It's designed for AEC
professionals working with complex Speckle data structures.
"""

from collections.abc import Iterable
from typing import Optional, Tuple, List

from specklepy.objects import Base
from specklepy.objects.other import Instance, Transform


def flatten_base(base: Base, parent_type: str = None) -> Iterable[Base]:
    """
    Flattens a Speckle object tree into an iterable of base objects.

    Args:
        base: The base object to flatten.
        parent_type: The type of the parent object, if applicable.

    Yields:
        Base: A flattened base object, making complex hierarchies linear.
    """
    if isinstance(base, Base):
        base["parent_type"] = parent_type

    # Handle collections of elements in the base object
    if hasattr(base, "elements") and base.elements:
        try:
            for element in base.elements:
                yield from flatten_base(element, base.speckle_type)
        except KeyError:
            pass
    # Handle older Revit-specific patterns with '@Lines'
    elif hasattr(base, "@Lines"):
        categories = base.get_dynamic_member_names()
        for category in categories:
            if category.startswith("@"):
                category_object: Base = getattr(base, category)[0]
                yield from flatten_base(category_object, category_object.speckle_type)
    else:
        yield base


def extract_base_and_transform(
    base: Base,
    inherited_instance_id: Optional[str] = None,
    transform_list: Optional[List[Transform]] = None,
) -> Tuple[Base, str, Optional[List[Transform]]]:
    """
    Extracts `Base` objects and their transformations from Speckle data.

    Args:
        base: The starting point `Base` object for traversal.
        inherited_instance_id: Inherited ID for objects without a unique one.
        transform_list: List of transformations from parent to child objects.

    Yields:
        tuple: A `Base` object, its identifier, and applicable transforms.
    """
    current_id = getattr(base, "id", inherited_instance_id)
    transform_list = transform_list or []

    if isinstance(base, Instance):
        if base.transform:
            transform_list.append(base.transform)
        if base.definition:
            yield from extract_base_and_transform(
                base.definition, current_id, transform_list.copy()
            )
    else:
        yield base, current_id, transform_list

        # Process 'elements' and '@elements' in the base object
        elements_attr = getattr(base, "elements", []) or getattr(base, "@elements", [])
        for element in elements_attr:
            if isinstance(element, Base):
                yield from extract_base_and_transform(
                    element, current_id, transform_list.copy()
                )

        # Process '@'-prefixed properties in older Speckle data models
        for attr_name in dir(base):
            if attr_name.startswith("@"):
                attr_value = getattr(base, attr_name)
                if isinstance(attr_value, Base) and hasattr(attr_value, "elements"):
                    yield from extract_base_and_transform(
                        attr_value, current_id, transform_list.copy()
                    )
