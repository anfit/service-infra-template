# Operator guide

## Local setup

Install `vps-deployer`, then define explicit roots for the application checkout
and this infrastructure checkout. The manifests intentionally do not rely on
repository traversal.

```powershell
$env:PROJECTS_DIR = 'C:\path\to\projects'
$env:SERVICE_INFRA_DIR = 'C:\path\to\service-infra'
$env:EXAMPLE_SERVICE_PROD_API_TOKEN = '<load from your secret store>'
```

On Linux or macOS, export the same variables with POSIX paths. Keep secrets in a
secret manager or protected user environment; `.env` files are ignored only as
a last line of defense.

## First deployment

From any directory, select this repository explicitly:

```powershell
vps-deployer --repo $env:SERVICE_INFRA_DIR validate
vps-deployer --repo $env:SERVICE_INFRA_DIR host inspect prod
vps-deployer --repo $env:SERVICE_INFRA_DIR host onboard prod
vps-deployer --repo $env:SERVICE_INFRA_DIR plan example-service-prod
vps-deployer --repo $env:SERVICE_INFRA_DIR apply example-service-prod
vps-deployer --repo $env:SERVICE_INFRA_DIR status example-service-prod
vps-deployer --repo $env:SERVICE_INFRA_DIR plan example-service-prod
```

The final plan should be a no-op. Host onboarding changes the remote machine, so
inspect its plan and the `vps-deployer` operations documentation first.

## Normal changes

1. Confirm the intended application branch, commit, and clean working tree.
2. Ensure the application `.vps-deployer-ignore` excludes local credentials and
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

## Before publishing changes

- Search tracked content for real domains, public IPs, usernames, email
  addresses, tokens, private-key material, and provider-specific hostnames.
- Verify that secret values occur nowhere in Git history.
- Confirm all secret-bearing settings use `secrets.<KEY>.from_env`.
- Keep production inventory and service-specific documentation out of public
  examples.
