# Operator guide

## Local setup

Install `vps-deployer` (`pipx install vps-deployer`, 1.3.1 or newer; upgrade with
`pipx upgrade vps-deployer`), then define explicit roots for the application
checkout and this infrastructure checkout. The manifests intentionally do not rely
on repository traversal.

```powershell
$env:PROJECTS_DIR = 'C:\path\to\projects'
$env:SERVICE_INFRA_DIR = 'C:\path\to\service-infra'
$env:EXAMPLE_SERVICE_PROD_API_TOKEN = '<load from your secret store>'
```

Secrets do not have to live in environment variables. From `vps-deployer` 1.4.0 a
variable is looked up in the environment, then in a user-only secrets file, and
optionally in the OS credential store. Store one without printing it, and see
where each variable resolves:

```powershell
vps-deployer secrets set EXAMPLE_SERVICE_PROD_API_TOKEN   # prompts; add --store keyring for the OS store
vps-deployer secrets sources
vps-deployer secrets list                     # every source holding each variable, plus leftovers
vps-deployer secrets rotate NAME               # new value, then which deployments to re-apply
vps-deployer secrets unset NAME                # delete a stored value
```

Stored values are per user and per machine and readable by any process you run;
keep your password manager as the source of truth. After rotating, `apply` each
deployment that `rotate` names.

On Linux or macOS, export the same variables with POSIX paths. Keep secrets in a
secret manager or protected user environment; `.env` files are ignored only as
a last line of defense.

## First deployment

From any directory, select this repository explicitly (or omit `--repo` when
`SERVICE_INFRA_DIR` is set):

```powershell
vps-deployer --repo $env:SERVICE_INFRA_DIR validate
vps-deployer --repo $env:SERVICE_INFRA_DIR secrets check
vps-deployer --repo $env:SERVICE_INFRA_DIR host inspect prod
vps-deployer --repo $env:SERVICE_INFRA_DIR host onboard prod
vps-deployer --repo $env:SERVICE_INFRA_DIR plan example-service-prod
vps-deployer --repo $env:SERVICE_INFRA_DIR apply example-service-prod
vps-deployer --repo $env:SERVICE_INFRA_DIR status example-service-prod
vps-deployer --repo $env:SERVICE_INFRA_DIR plan example-service-prod
```

The final plan should be a no-op. Host onboarding changes the remote machine, so
inspect its plan and the `vps-deployer` operations documentation first.

## Hosts that use the privileged SSH gate

If a host sets `ssh.privileged_host`, its privileged key must be restricted by the
`vps-deployer-ssh-gate` forced command. Print the exact setup, including the
`authorized_keys` line derived from this repository's manifests, with:

```powershell
vps-deployer host bootstrap prod            # print the steps
vps-deployer host bootstrap prod --install  # also copy the gate (needs passwordless sudo)
vps-deployer host inspect prod              # reports gate: ok | mismatch | outdated | none
```

`host inspect` exits 1 on a gate `mismatch` or `outdated`, so reinstall the gate
after upgrading `vps-deployer` before running `apply`.

## Fleet overview

```powershell
vps-deployer list                        # offline inventory from the manifests
vps-deployer status --all                # state (ok/down) and source (in sync / deploy pending)
vps-deployer plan --all --exit-code      # exit 1 if any deployment has pending changes
python tools/update-services-doc.py      # refresh the generated block in docs/services.md
```

Run `vps-deployer init app <dir>` to create a `.deployer/` contract for a new
application and `vps-deployer doctor <dir>` to check one before deploying.

## Normal changes

1. Confirm the intended application branch, commit, and clean working tree.
2. Ensure the application `.deployer/ignore.txt` excludes local credentials and
   development-only files.
3. Run `validate`, then review `plan`.
4. Run `apply`, then `status`.
5. Exercise the health endpoint and public route.
6. Run `plan` again and require a no-op result.

## Recovery

```powershell
vps-deployer --repo $env:SERVICE_INFRA_DIR logs example-service-prod --lines 200
vps-deployer --repo $env:SERVICE_INFRA_DIR rollback example-service-prod
```

Rollback activates the retained predecessor release. It does not modify desired
state in this repository. Reconcile the manifest or application source afterward.
Until then `plan` shows `ACTIVATE` marked as reversing a manual rollback.

## Common failures

- **`secret environment variables not set`**: run `secrets check`; a terminal
  opened before you set a persistent variable will not see it.
- **`runtime executable is missing from release`**: the application lacks an
  executable `.deployer/run.sh`, or `.deployer/ignore.txt` excludes it.
- **Health check failed; previous release restored**: inspect `logs`. Typical
  causes are CRLF line endings or a bad shebang in shell scripts (enforce LF
  with `.gitattributes`), a missing runtime dependency, or a port collision.
- **Plan keeps proposing changes after `apply`**: a manual `rollback` does not
  change desired state, so the plan proposes reactivating the desired release.

## Before publishing changes

- Search tracked content for real domains, public IPs, usernames, email
  addresses, tokens, private-key material, and provider-specific hostnames.
- Verify that secret values occur nowhere in Git history.
- Confirm all secret-bearing settings use `secrets.<KEY>.from_env`.
- Keep production inventory and service-specific documentation out of public
  examples.
