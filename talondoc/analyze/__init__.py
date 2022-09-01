import pathlib
import typing

from ..shims import talon_shims
from ..types import FileEntry, PackageEntry
from .python import analyse_python_file, python_package
from .registry import Registry
from .talon import analyse_talon_file


def match(
    file_path: pathlib.Path,
    *,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
) -> bool:
    return (
        not exclude
        or not any(file_path.match(exclude_pattern) for exclude_pattern in exclude)
        or any(file_path.match(include_pattern) for include_pattern in include)
    )


def analyse_package(
    registry: Registry,
    package_root: pathlib.Path,
    *,
    name: typing.Optional[str] = None,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
) -> PackageEntry:
    package_entry = PackageEntry(name=name, path=package_root.absolute())
    with talon_shims(registry):
        with python_package(package_entry):
            for file_path in package_entry.path.glob("**/*"):
                file_path = file_path.relative_to(package_entry.path)
                if match(file_path, include=include, exclude=exclude):
                    file_entry = analyse_file(registry, file_path, package_entry)
                    if file_entry:
                        package_entry.files.append(file_entry)

            # Register package:
            registry.register(package_entry)
            return package_entry


def analyse_file(
    registry: Registry, file_path: pathlib.Path, package_entry: PackageEntry
) -> typing.Optional[FileEntry]:
    if file_path.match("*.py"):
        return analyse_python_file(registry, file_path, package_entry)
    # elif file_path.match("*.talon"):
    #     return analyse_talon_file(registry, file_path, package_entry)
    else:
        return None