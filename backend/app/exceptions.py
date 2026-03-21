
class KraytourException(Exception):
    """Base class for all custom exceptions in the Kraytour application."""
    pass

class LocationNotFoundError(KraytourException):
    """Raised when a requested location is not found in the database."""
    def __init__(self, location_id: int):
        self.location_id = location_id
        super().__init__(f"Location with ID {location_id} not found.")
        
class LocationSlugAlreadyExistsError(KraytourException):
    """Raised when trying to create a location with a slug that already exists."""
    def __init__(self, slug: str):
        self.slug = slug
        super().__init__(f"Location with slug '{slug}' already exists.")
        
class LocationTagsNotFoundError(KraytourException):
    """Raised when one or more tags specified for a location are not found."""
    def __init__(self, tag_ids: list[int]):
        self.tag_ids = tag_ids
        super().__init__(f"Tags with IDs {tag_ids} not found.")