#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: Apache-2.0
import logging
from collections.abc import Sequence
from typing import Final

from ..exceptions import SmithyIdentityException
from .interfaces.identity import IdentityResolver

logger: Final = logging.getLogger(__name__)


class ChainedIdentityResolver[I, IP](IdentityResolver[I, IP]):
    """Attempts to resolve an identity by checking a sequence of sub-resolvers.

    If a nested resolver raises a :py:class:`SmithyIdentityException`, the next
    resolver in the chain will be attempted.
    """

    def __init__(self, resolvers: Sequence[IdentityResolver[I, IP]]) -> None:
        """Construct a ChainedIdentityResolver.

        :param resolvers: The sequence of resolvers to resolve identity from.
        """
        self._resolvers = resolvers

    async def get_identity(self, *, properties: IP) -> I:
        logger.debug("Attempting to resolve identity from resolver chain.")
        for resolver in self._resolvers:
            try:
                logger.debug("Attempting to resolve identity from %s.", type(resolver))
                return await resolver.get_identity(properties=properties)
            except SmithyIdentityException as e:
                logger.debug(
                    "Failed to resolve identity from %s: %s", type(resolver), e
                )

        raise SmithyIdentityException("Failed to resolve identity from resolver chain.")
