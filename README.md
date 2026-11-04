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
4. Install the tool: `pipx install vps-deployer`.
5. Set `PROJECTS_DIR` and `SERVICE_INFRA_DIR` to absolute local paths. With
   `SERVICE_INFRA_DIR` set, `vps-deployer` finds this repository from any
   directory, so `--repo` is optional.
6. Set every environment variable referenced by `secrets.*.from_env`; the names
   are listed in `.env.example`. Keep that file in step with the manifests.
7. Validate before connecting to a host:

   ```powershell
   vps-deployer validate
   vps-deployer secrets check
   vps-deployer list
   ```

8. Refresh the generated inventory in `docs/services.md` after changing
   deployments: `python tools/update-services-doc.py`.

Continue with [the operator guide](docs/operator-guide.md). For the complete
schema and security model, see the `vps-deployer` documentation.

The corresponding application artifact should provide an executable
`.deployer/run.sh`, an optional `.deployer/ignore.txt`, and, when needed,
read-only host assumptions in `.deployer/expect.yaml`. The default runtime
command uses `.deployer/run.sh`, so ordinary manifests do not repeat that
application-owned path.

## Repository layout

```text
hosts/                         # SSH identity and managed root per host
tools/                         # helper scripts (parity check, services.md generator)
deployments/                   # desired state, grouped by application
configs/                       # optional committed, non-secret app config
globals/                       # optional shared, non-secret values
docs/                          # operator-specific documentation
```

## Staying in sync with a derived repository

If you keep a private instance derived from this template, mirror generic
changes (docs, tooling, layout) in both. `tools/check-template-parity.py`
compares the two checkouts and reports only unexpected drift:

```powershell
python tools/check-template-parity.py --instance <your infra repo> --template <this repo>
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
