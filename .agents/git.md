# Git Commit Style

When writing commit messages, always use a bullet list in the body to describe
the individual changes. Never write the body as prose.


## Format

```text
<type>(<scope>): <short description>

- <change 1>
- <change 2>
- <change 3>
```

The short description is lowercase and does not end with a period. Each bullet
describes one logical change concisely, also lowercase, no trailing period.


## Example

```text
ci: address cybersecurity findings for docker image vulnerabilities

- upgrade postgres service container from 16 to 17 in app-ci.yml
- switch node base image from alpine3.23 to alpine, patch picomatch GHSA-c2c7-rcm5-vvqj
- replace docs base image with ubuntu:24.04, install uv via COPY --from
- migrate sbom.yml from curl+syft install to anchore/sbom-action
- add docker-scan.yml workflow using anchore/scan-action on Dockerfile.base
- add infra/scripts/collect-docker-images.py to extract base image for scan workflow
```
