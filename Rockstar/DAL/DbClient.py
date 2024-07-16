import os
from supabase import create_client


class DbClient:
    def __init__(self):
        self.client = create_client(os.environ['DB_URL'], os.environ['DB_KEY'])

    def get_table(self, table_name, select_filter="*"):
        return self.client.table(table_name).select(select_filter).execute().data

    def get_filter_table(self, table_name, filter_name, filter_value, select_filter="*"):
        return self.client.table(table_name).select(select_filter).eq(filter_name, filter_value).execute().data

    def insert_data(self, table_name, data):
        return self.client.table(table_name).insert(data).execute().data

    def update_data(self, table_name, data, filter_name, filter_value):
        return self.client.table(table_name).update(data).eq(filter_name, filter_value).execute().data

    def delete_row(self, table_name, filter_name, filter_value):
        return self.client.table(table_name).delete().eq(filter_name, filter_value).execute().data
