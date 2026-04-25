# Wieliczka Kiedy Odpady

Support for schedules provided by [Wieliczka Kiedy Odpady](https://wieliczka.kiedyodpady.pl), Poland.

## Configuration via configuration.yaml

```yaml
waste_collection_schedule:
  sources:
    - name: wieliczka_kiedyodpady_pl
      args:
        city: Wieliczka (miasto)
        street: ul. Adama Asnyka
        number: pozostałe
```

### Configuration Variables

**number**  
*(String) (required)* House number/address entry from the selected street.

**city**  
*(String) (required)* City name.

**street**  
*(String) (required)* Street name.

## Example

```yaml
waste_collection_schedule:
  sources:
    - name: wieliczka_kiedyodpady_pl
      args:
        city: "Wieliczka (miasto)"
        street: "ul. Adama Asnyka"
        number: "pozostałe"
```

## How to get the source argument

1. Fetch cities from:
   `https://api.kiedyodpady.pl/public/territory/localities`
2. Fetch streets for a city:
   `https://api.kiedyodpady.pl/public/territory/localities/<locality_id>/streets`
3. Fetch house numbers for a street:
   `https://api.kiedyodpady.pl/public/territory/localities/<locality_id>/addresses/<street_id>`

All API requests must include header:

```text
Origin: https://wieliczka.kiedyodpady.pl
```
