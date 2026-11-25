#!/usr/bin/env python3

import json
from pathlib import Path, PurePosixPath


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    providers = (root / "iosApp" / "BundledProviders").resolve()
    manifest_path = providers / "manifest.json"
    if not providers.exists():
        print("No bundled providers configured for TestFlight.")
        return

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for field in ("name", "version"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            raise ValueError(f"Provider manifest requires a nonempty {field}.")
    if not isinstance(manifest.get("scrapers"), list) or not manifest["scrapers"]:
        raise ValueError("Provider manifest requires a nonempty scrapers list.")

    scripts = {}
    provider_ids = set()
    for scraper in manifest["scrapers"]:
        for field in ("id", "name", "version", "filename"):
            if not isinstance(scraper.get(field), str) or not scraper[field].strip():
                raise ValueError(f"Every provider requires a nonempty {field}.")
        provider_id = scraper["id"]
        if provider_id in provider_ids:
            raise ValueError(f"Duplicate provider id: {provider_id}")
        provider_ids.add(provider_id)

        filename = scraper["filename"]
        relative = PurePosixPath(filename)
        script_path = (providers / relative).resolve()
        if (relative.is_absolute() or ".." in relative.parts or ":" in filename or "\\" in filename
                or relative.suffix != ".js" or not script_path.is_relative_to(providers)):
            raise ValueError(f"Provider script must be a local JavaScript file: {filename}")
        code = script_path.read_text(encoding="utf-8")
        if not code.strip():
            raise ValueError(f"Provider script is empty: {filename}")
        scripts[filename] = code

    destination = root / "iosApp" / "iosApp" / "NuvioBundledProviders.json"
    destination.write_text(json.dumps({"manifest": manifest, "scripts": scripts}), encoding="utf-8")
    print(f"Bundled {len(provider_ids)} provider(s) for TestFlight.")


if __name__ == "__main__":
    main()
