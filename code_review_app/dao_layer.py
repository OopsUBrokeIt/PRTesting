from code_review_app.clients import HostsServiceClient, ListingServiceClient
from code_review_app.dao import HostDAO, ListingDAO, ListingWithHostDAO


class ListingDAOReader:
    def __init__(
        self,
        listings_client: ListingServiceClient,
        hosts_client: HostsServiceClient,
    ) -> None:
        self._listings_client = listings_client
        self._hosts_client = hosts_client

    def get_listing_with_host(self, listing_id: str) -> ListingWithHostDAO | None:
        listing_raw = self._listings_client.fetch_listing(listing_id)
        if listing_raw is None:
            return None

        host_raw = self._hosts_client.fetch_host(listing_raw["host_id"])
        if host_raw is None:
            return None

        listing_dao = ListingDAO(
            listing_id=listing_raw["id"],
            host_id=listing_raw["host_id"],
            title=listing_raw["title"],
            nightly_price_usd=listing_raw["nightly_price_usd"],
        )
        host_dao = HostDAO(
            host_id=host_raw["id"],
            host_name=host_raw["name"],
            is_superhost=host_raw["superhost"],
        )
        return ListingWithHostDAO(listing=listing_dao, host=host_dao)
