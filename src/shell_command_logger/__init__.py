def get_name_and_version() -> tuple[str, str]:
    from importlib_metadata import version

    package_name = __package__
    package_version = version(package_name)

    return (package_name, package_version)

def get_version_string() -> str:
    name, version = get_name_and_version()
    return f"{name} {version or 'N/A'}"
