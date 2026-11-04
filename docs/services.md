# Managed services

## Hosts

| Host | Connection | Purpose |
| --- | --- | --- |
| `prod` | `deploy@prod-vps` | Replace with your host description |

## Notes

Record ownership, public URLs, operational exceptions and anything the manifests
cannot express. The inventory below is generated from the manifests.

## Generated inventory

Generated from the manifests; do not edit between the markers. Regenerate with `python tools/update-services-doc.py`.

<!-- BEGIN GENERATED INVENTORY (tools/update-services-doc.py) -->
| deployment | host | kind | user | ingress | storage | secret variables |
|---|---|---|---|---|---|---|
| `example-service-prod` | `prod` | service | `svc-example` | service.example.com | `/var/lib/example-service` | `EXAMPLE_SERVICE_PROD_API_TOKEN` |
<!-- END GENERATED INVENTORY -->
