import builtins
from typing_extensions import NotRequired, AsyncIterable
from dataclasses import dataclass
from decimal import Decimal

from binance.core import AuthEndpoint, validator, TypedDict

class LockedProductDetail(TypedDict):
  asset: str
  """Asset name"""
  rewardAsset: NotRequired[str]
  """Reward asset (omitted when only extra reward is present)"""
  duration: int
  """Lock duration in days"""
  renewable: bool
  """Whether the product is renewable"""
  isSoldOut: bool
  """Whether the product is sold out"""
  apr: NotRequired[Decimal]
  """Annual percentage rate (omitted when only extra reward APR is present)"""
  status: str
  """Product status"""
  subscriptionStartTime: int
  """Subscription start time (milliseconds)"""
  extraRewardAsset: NotRequired[str]
  """Extra reward asset"""
  extraRewardAPR: NotRequired[Decimal]
  """Extra reward APR"""
  boostRewardAsset: NotRequired[str]
  """Boost reward asset"""
  # API returns boostRewardApr; docs example uses "boostApr"
  boostRewardApr: NotRequired[Decimal]
  """Boost reward APR"""
  boostEndTime: NotRequired[int]
  """Boost end time (milliseconds)"""

class LockedProductQuota(TypedDict):
  totalPersonalQuota: Decimal
  """Total personal quota"""
  minimum: Decimal
  """Minimum subscription amount"""

class LockedProductRow(TypedDict):
  projectId: str
  """Project identifier"""
  detail: LockedProductDetail
  """Product detail"""
  quota: LockedProductQuota
  """Subscription quota"""

class LockedListResponse(TypedDict):
  rows: list[LockedProductRow]
  """List of locked products"""
  total: int
  """Total count"""

validate_response = validator(LockedListResponse)

@dataclass
class LockedList(AuthEndpoint):
  async def list(
    self,
    *,
    asset: str | None = None,
    current: int | None = None,
    size: int | None = None,
    recv_window: int | None = None,
    validate: bool | None = None
  ):
    """Get available Simple Earn locked product list.

    - `asset`: Filter by asset
    - `current`: Currently querying page. Start from 1. Default: 1
    - `size`: Page size. Default: 10, Max: 100
    - `recv_window`: Request receive window (milliseconds)
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [Binance API docs](https://developers.binance.com/docs/simple_earn/flexible-locked/account/Get-Simple-Earn-Locked-Product-List)
    """
    params: dict = {}
    if asset is not None:
      params['asset'] = asset
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    if recv_window is not None:
      params['recvWindow'] = recv_window
    r = await self.authed_request('GET', '/sapi/v1/simple-earn/locked/list', params=params)
    return self.output(r.text, validate_response, validate=validate)


  async def list_paged(
    self,
    *,
    asset: str | None = None,
    size: int = 100,
    recv_window: int | None = None,
    validate: bool | None = None
  ) -> AsyncIterable[builtins.list[LockedProductRow]]:
    """Get available Simple Earn locked product list.
    """
    current = 1
    while True:
      r = await self.list(asset=asset, current=current, size=size, recv_window=recv_window, validate=validate)
      if not r['rows']:
        break
      yield r['rows']
      if r['total'] <= current*size:
        break
      current += 1
