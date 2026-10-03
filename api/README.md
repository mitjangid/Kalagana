# Kalagana API — import files

Ready-to-import client collections and a machine-readable spec for the Kalagana
local REST API. See [`../API_README.md`](../API_README.md) for the full endpoint
reference.

Start the server first:

```bash
python -m kalagana.server --port 8765   # or: python -m kalagana serve
```

Every client below points at `{{baseUrl}}` / `{{ _.baseUrl }}` = `http://127.0.0.1:8765`.

| File | Tool | How to import |
|---|---|---|
| [`openapi.json`](openapi.json) | OpenAPI 3.1 | Postman → Import → File; Insomnia → Import; Swagger UI; `openapi-generator` |
| [`postman/Kalagana.postman_collection.json`](postman/Kalagana.postman_collection.json) | Postman | Import → File |
| [`postman/Kalagana.postman_environment.json`](postman/Kalagana.postman_environment.json) | Postman | Environments → Import; select **Kalagana Local** |
| [`insomnia/Kalagana.insomnia.json`](insomnia/Kalagana.insomnia.json) | Insomnia | Import Data → From File |
| [`bruno/`](bruno) | Bruno | Open Collection → select the `bruno` folder |

## Coverage

| Group | Requests |
|---|---|
| Meta | `/health`, `/cities`, `/ayanamsas` |
| Panchang | `/day` (built-in city, custom lat/lon, no-muhurta), `/month` |
| Festivals | `/festivals` (tradition + `major_only`), `/find` |
| Events | `/eclipses` |
| Muhurta | `/muhurta` |

The Postman collection also includes a small **Errors** folder demonstrating the
`400` shapes for a missing date and a missing location.
