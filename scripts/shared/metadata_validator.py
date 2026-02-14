"""
Metadata validation utilities for work import scripts.

This module provides validation for work metadata to ensure all required fields
are present with correct types and values before database insertion.

Usage:
    from shared.metadata_validator import MetadataValidator

    validator = MetadataValidator()
    validator.validate(metadata_dict, work_key='work_1')
    # Raises ValueError if validation fails

See scripts/metadata/README.md for complete metadata schema specification.
"""


class MetadataValidator:
    """Validates work metadata against schema requirements."""

    # Fields that MUST be present in every work metadata entry
    REQUIRED_FIELDS = {
        'work_name': str,
        'work_name_tamil': str,
        'canonical_order': int,
        'position_in_collection': int,
        'chronology_start_year': int,
    }

    # Fields that MAY be present (validated if they exist)
    OPTIONAL_FIELDS = {
        'chronology_end_year': int,
        'chronology_confidence': str,
        'chronology_notes': str,
        'author': str,
        'author_tamil': str,
        'period': str,
        'description': str,
    }

    # Valid values for chronology_confidence field
    VALID_CONFIDENCE_VALUES = {'high', 'medium', 'low'}

    def validate(self, metadata: dict, work_key: str) -> None:
        """
        Validate a single work's metadata.

        Args:
            metadata: Dictionary containing work metadata
            work_key: Identifier for the work (for error messages)

        Raises:
            ValueError: If validation fails (lists all errors found)
        """
        errors = []

        # Check all required fields are present with correct types
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in metadata:
                errors.append(f"Missing required field: {field}")
            elif metadata[field] is None:
                errors.append(f"Required field '{field}' cannot be None")
            elif not isinstance(metadata[field], expected_type):
                actual_type = type(metadata[field]).__name__
                expected_name = expected_type.__name__
                errors.append(
                    f"{field} must be {expected_name}, got {actual_type} "
                    f"(value: {repr(metadata[field])})"
                )

        # Validate optional fields if present
        for field, expected_type in self.OPTIONAL_FIELDS.items():
            if field in metadata and metadata[field] is not None:
                if not isinstance(metadata[field], expected_type):
                    actual_type = type(metadata[field]).__name__
                    expected_name = expected_type.__name__
                    errors.append(
                        f"{field} must be {expected_name}, got {actual_type}"
                    )

        # Special validation: chronology_confidence must be valid value
        if 'chronology_confidence' in metadata and metadata['chronology_confidence'] is not None:
            conf = metadata['chronology_confidence']
            if conf not in self.VALID_CONFIDENCE_VALUES:
                errors.append(
                    f"chronology_confidence must be one of "
                    f"{self.VALID_CONFIDENCE_VALUES}, got '{conf}'"
                )

        # Special validation: end year must be >= start year
        if ('chronology_end_year' in metadata and
            'chronology_start_year' in metadata and
            metadata['chronology_end_year'] is not None and
            metadata['chronology_start_year'] is not None):
            if metadata['chronology_end_year'] < metadata['chronology_start_year']:
                errors.append(
                    f"chronology_end_year ({metadata['chronology_end_year']}) "
                    f"cannot be before start_year ({metadata['chronology_start_year']})"
                )

        # Special validation: canonical_order should be positive (only check if type is correct)
        if ('canonical_order' in metadata and
            metadata['canonical_order'] is not None and
            isinstance(metadata['canonical_order'], int)):
            if metadata['canonical_order'] <= 0:
                errors.append(
                    f"canonical_order must be positive, got {metadata['canonical_order']}"
                )

        # Special validation: position_in_collection should be positive (only check if type is correct)
        if ('position_in_collection' in metadata and
            metadata['position_in_collection'] is not None and
            isinstance(metadata['position_in_collection'], int)):
            if metadata['position_in_collection'] <= 0:
                errors.append(
                    f"position_in_collection must be positive, "
                    f"got {metadata['position_in_collection']}"
                )

        # If any errors found, raise ValueError with all details
        if errors:
            error_msg = f"Metadata validation failed for work '{work_key}':\n"
            error_msg += "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)

    def validate_all(self, work_metadata: dict) -> None:
        """
        Validate all works in a metadata dictionary.

        Args:
            work_metadata: Dictionary mapping work keys to metadata dicts

        Raises:
            ValueError: If validation fails for any work (stops at first error)

        Example:
            validator = MetadataValidator()
            validator.validate_all(WORK_METADATA)
        """
        for work_key, metadata in work_metadata.items():
            self.validate(metadata, work_key)

    def validate_collection_metadata(
        self,
        work_metadata: dict,
        collection_id: int,
        collection_name: str,
        collection_name_tamil: str
    ) -> None:
        """
        Validate complete collection metadata including collection-level fields.

        Args:
            work_metadata: Dictionary of work metadata entries
            collection_id: Collection ID
            collection_name: English collection name
            collection_name_tamil: Tamil collection name

        Raises:
            ValueError: If validation fails
        """
        errors = []

        # Validate collection-level fields
        if not isinstance(collection_id, int) or collection_id <= 0:
            errors.append(f"collection_id must be positive integer, got {collection_id}")

        if not isinstance(collection_name, str) or not collection_name.strip():
            errors.append(f"collection_name must be non-empty string")

        if not isinstance(collection_name_tamil, str) or not collection_name_tamil.strip():
            errors.append(f"collection_name_tamil must be non-empty string")

        if errors:
            error_msg = "Collection metadata validation failed:\n"
            error_msg += "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)

        # Validate all works
        self.validate_all(work_metadata)

        # Additional validation: check for duplicate canonical_order values
        canonical_orders = {}
        for work_key, metadata in work_metadata.items():
            order = metadata.get('canonical_order')
            if order in canonical_orders:
                errors.append(
                    f"Duplicate canonical_order {order} found in works "
                    f"'{canonical_orders[order]}' and '{work_key}'"
                )
            else:
                canonical_orders[order] = work_key

        # Additional validation: check for duplicate position_in_collection values
        positions = {}
        for work_key, metadata in work_metadata.items():
            pos = metadata.get('position_in_collection')
            if pos in positions:
                errors.append(
                    f"Duplicate position_in_collection {pos} found in works "
                    f"'{positions[pos]}' and '{work_key}'"
                )
            else:
                positions[pos] = work_key

        if errors:
            error_msg = f"Collection '{collection_name}' validation failed:\n"
            error_msg += "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)


# Convenience function for quick validation
def validate_metadata(metadata: dict, work_key: str = 'unknown') -> None:
    """
    Convenience function to validate a single work's metadata.

    Args:
        metadata: Work metadata dictionary
        work_key: Identifier for the work (for error messages)

    Raises:
        ValueError: If validation fails
    """
    validator = MetadataValidator()
    validator.validate(metadata, work_key)
