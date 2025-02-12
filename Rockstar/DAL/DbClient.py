import os

from supabase import create_client, ClientOptions


class DbClient:
    def __init__(self):
        self.client = create_client(
            os.environ['DB_URL'], os.environ['DB_KEY'],
            ClientOptions(postgrest_client_timeout=999999, storage_client_timeout=999999)
        )

    def get_table(self, table_name, select_filter="*"):
        return self.client.table(table_name).select(select_filter).execute().data

    def get_filter_table(self, table_name, filter_name, filter_value, select_filter="*"):
        query = self.client.table(table_name).select(select_filter)
        if isinstance(filter_value, list):
            query = query.in_(filter_name, filter_value)
        else:
            query = query.eq(filter_name, filter_value)
        return query.execute().data

    def insert_data(self, table_name, data):
        """Supports batch inserts by accepting a list of records."""
        if not isinstance(data, list):
            data = [data]
        return self.client.table(table_name).insert(data, upsert=True).execute().data

    def update_data(self, table_name, data, filter_name, filter_values):
        """Supports batch updates by accepting a list of filter values."""
        if not isinstance(filter_values, list):
            filter_values = [filter_values]
        return self.client.table(table_name).update(data).in_(filter_name, filter_values).execute().data

    def delete_row(self, table_name, filter_name, filter_value):
        return self.client.table(table_name).delete().eq(filter_name, filter_value).execute().data
