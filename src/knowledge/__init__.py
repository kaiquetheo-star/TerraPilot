"""Base de conhecimento contextual para o produtor rural."""

from .knowledge_service import (
    ProducerProfile,
    get_contextual_faq,
    list_knowledge_asset_paths,
)

__all__ = [
    "ProducerProfile",
    "get_contextual_faq",
    "list_knowledge_asset_paths",
]
