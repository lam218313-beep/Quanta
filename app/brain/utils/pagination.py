"""
Shared Supabase pagination helper.
PostgREST caps a single request at 1000 rows; this walks the full result set
in pages so callers can request an entire table/query without hitting that limit.
"""


class MockResponse:
    """Mimics the shape of a supabase-py response (.data) for the merged pages."""
    def __init__(self, data):
        self.data = data


def fetch_all_records(table, supabase_client, select="*", eq_filters=None, order_by=None):
    if eq_filters is None:
        eq_filters = {}
    all_data = []
    page = 0
    page_size = 1000
    while True:
        query = supabase_client.table(table).select(select)
        for k, v in eq_filters.items():
            query = query.eq(k, v)
        if order_by:
            query = query.order(order_by)

        query = query.range(page * page_size, (page + 1) * page_size - 1)
        res = query.execute()

        if not res.data:
            break
        all_data.extend(res.data)
        if len(res.data) < page_size:
            break
        page += 1
    return MockResponse(all_data)
