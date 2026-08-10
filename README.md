# service-infra-template

A safe starting point for a private infrastructure repository managed by
`vps-deployer`.

This template keeps host identity separate from deployment identity and shows
how to deploy a systemd service with persistent storage, an HTTP health check,
an nginx route, committed non-secret configuration, and secrets supplied only
through the operator's environment.

## Use this template

1. Create a **private** repository from this template and clone it.
2. Replace the placeholder values in `hosts/prod.yaml`.
3. Rename and adapt `deployments/example-service/prod.yaml`.
4. Set `PROJECTS_DIR` and `SERVICE_INFRA_DIR` to absolute local paths.
5. Set every environment variable referenced by `secrets.*.from_env`.
6. Validate before connecting to a host:

   ```powershell
   vps-deployer --repo $env:SERVICE_INFRA_DIR validate
   ```

Continue with [the operator guide](docs/operator-guide.md). For the complete
schema and security model, see the `vps-deployer` documentation.

## Repository layout

```text
hosts/                         # SSH identity and managed root per host
deployments/                   # desired state, grouped by application
configs/                       # optional committed, non-secret app config
globals/                       # optional shared, non-secret values
docs/                          # operator-specific documentation
```

## Security boundary

- Keep this infrastructure repository private even when `vps-deployer` is public.
- Commit secret references, never secret values.
- Do not commit `.env` files, private keys, credentials, host inventories, or
  production data.
- Review every `plan` before `apply`.
- Use a dedicated SSH identity and the deployer's forced-command SSH gate for
  privileged operations.
- Treat generated plans, logs, and copied production configuration as sensitive.

All names, domains, addresses, paths, and credentials in this repository are
deliberate placeholders.
