# Wieliczka Kiedy Odpady

Support for schedules provided by [Wieliczka Kiedy Odpady](https://wieliczka.kiedyodpady.pl), Poland.

## Configuration via configuration.yaml

```yaml
waste_collection_schedule:
  sources:
    - name: wieliczka_kiedyodpady_pl
      args:
        locality: Wieliczka
        street: Asnyka
        number: pozostałe
```

### Configuration Variables

**number**  
*(String) (required)* House number/address entry from the selected street.

**locality**  
*(String) (required if locality_id not provided)* Locality name.

**locality_id**  
*(String) (required if locality not provided)* Locality ID.

**street**  
*(String) (required if street_id not provided)* Street name.

**street_id**  
*(String) (required if street not provided)* Street ID.

**property_type**  
*(String) (optional)* Extra API field, defaults to empty string.

**building_type**  
*(String) (optional)* Extra API field, defaults to empty string.

**days**  
*(Integer) (optional)* Number of days to fetch from today. Default is `35`.

## Example

```yaml
waste_collection_schedule:
  sources:
    - name: wieliczka_kiedyodpady_pl
      args:
        locality_id: "0952232"
        street_id: "15775"
        number: "pozostałe"
```

## How to get the source argument

1. Fetch localities from:
   `https://api.kiedyodpady.pl/public/territory/localities`
2. Fetch streets for a locality:
   `https://api.kiedyodpady.pl/public/territory/localities/<locality_id>/streets`
3. Fetch house numbers for a street:
   `https://api.kiedyodpady.pl/public/territory/localities/<locality_id>/addresses/<street_id>`

All API requests must include header:

```text
Origin: https://wieliczka.kiedyodpady.pl
```
