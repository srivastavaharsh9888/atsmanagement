from django.db.models import Q

class QueryBuilder:
    def __init__(self, model, payload):
        self.model = model
        self.payload = payload
        self.queryset = self.model.objects.all()
        self.relevance = {}

    def get_field_name(self, item):
        keys_to_be_excluded = ["search_type", "not_equals"]
        for key in item.keys():
            if key not in keys_to_be_excluded:
                return key
        return None

    def apply_filters(self):
        query = Q()
        for item in self.payload.get('filters', []):
            field = self.get_field_name(item)
            value = item[field]
            field_lookup = field.replace('.', '__')

            if isinstance(value, dict):  # Range queries like gte, lte
                for range_key, range_value in value.items():
                    lookup = f'{field_lookup}__{range_key}'
                    query &= Q(**{lookup: range_value})
            else:
                query = self.add_search_type(query, field_lookup, value, item)

        self.queryset = self.queryset.filter(query)

    def add_search_type(self, query, field, value, item):
        # Handling 'like', 'ilike', and 'not_equals'
        if 'search_type' in item:
            if item['search_type'] == 'like':
                query &= Q(**{f'{field}__contains': value})
            elif item['search_type'] == 'ilike':
                query &= Q(**{f'{field}__icontains': value})
        else:
            # Regular condition when 'search_type' is not present
            query &= Q(**{field: value})

        # Applying 'not_equals' if present, negating the entire constructed query
        if 'not_equals' in item and item['not_equals']:
            query = ~query

        return query

    def apply_sorting(self):
        sort_fields = self.payload.get('sort', {})
        if sort_fields:
            order_fields = []
            for field, order in sort_fields.items():
                # Replace '.' with '__' for related field sorting
                field = field.replace('.', '__')
                order_field = f"{'' if order == 'asc' else '-'}{field}"
                print(order_field)
                order_fields.append(order_field)
            self.queryset = self.queryset.order_by(*order_fields)

    def get_query(self):
        self.apply_filters()
        self.apply_sorting()
        return self.queryset
