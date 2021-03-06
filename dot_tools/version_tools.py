import bidict
import enum
import json
import os
import pydon
import re
from loguru import logger

from dot_tools.misc_tools import DotException
from dot_tools.git_tools import GitManager


DEFAULT_METADATA_FILE = (".project_metadata.py",)


class VersionError(DotException):
    pass


class VersionType(enum.IntEnum):
    major = 1
    minor = 2
    patch = 3
    release_candidate = 4
    beta = 5
    alpha = 6

    @classmethod
    def short_dict(cls):
        return bidict.bidict(
            M=cls.major,
            m=cls.minor,
            p=cls.patch,
            a=cls.alpha,
            b=cls.beta,
            rc=cls.release_candidate,
        )

    @classmethod
    def all_names(cls):
        return [e.name for e in cls]

    @classmethod
    def all_keys(cls):
        return [e.name for e in cls] + [k for k in cls.short_dict()]

    @classmethod
    def special(cls):
        return [e for e in cls if e > cls.patch]

    @classmethod
    def lookup(cls, key):
        key = key.lower()
        return cls.short_dict().get(key) or getattr(cls, key)


class Version:
    def __init__(self, *args, **kwargs):
        if len(args) > 0 or len(kwargs) > 0:
            self.set_version(*args, **kwargs)
        else:
            self.set_version(0, 0, 0)

    def update_from_string(self, text):
        match = re.match(
            r"^v?(\d+)\.(\d+)\.(\d+)(?:-(\w+)(\d+))?$",
            text,
        )
        VersionError.require_condition(
            match is not None,
            "Couldn't parse version",
        )
        self.set_version(*match.groups())

    def __repr__(self):
        text = "{}.{}.{}".format(
            self.d[VersionType.major],
            self.d[VersionType.minor],
            self.d[VersionType.patch],
        )
        if self.current_special_type is not None:
            text = "{}-{}{}".format(
                text,
                VersionType.short_dict().inv[self.current_special_type],
                self.d[self.current_special_type],
            )
        return text

    def __str__(self):
        return "v" + repr(self)

    def major_minor(self):
        return "{}.{}".format(
            self.d[VersionType.major],
            self.d[VersionType.minor],
        )

    @property
    def current_special_type(self):
        for special_type in VersionType.special():
            if self.d.get(special_type) is not None:
                return special_type
        return None

    def set_version(
        self, major_num, minor_num, patch_num, extra_type=None, extra_num=None
    ):
        self.d = {
            VersionType.major: int(major_num),
            VersionType.minor: int(minor_num),
            VersionType.patch: int(patch_num),
        }

        if extra_type is not None:
            with VersionError.handle_errors("Can't parse extra version info"):
                if not isinstance(extra_type, VersionType):
                    extra_type = VersionType.lookup(extra_type)
                self.d[extra_type] = int(extra_num)

    def bump(self, bump_type=VersionType.patch):
        logger.debug("Bumping version with type {}", bump_type)
        if not isinstance(bump_type, VersionType):
            bump_type = VersionType.lookup(bump_type)

        if bump_type is VersionType.major:
            self.set_version(self.d[VersionType.major] + 1, 0, 0)

        elif bump_type is VersionType.minor:
            self.set_version(
                self.d[VersionType.major], self.d[VersionType.minor] + 1, 0
            )

        elif bump_type is VersionType.patch:
            current_type = self.current_special_type
            if self.current_special_type is not None:
                self.set_version(
                    self.d[VersionType.major],
                    self.d[VersionType.minor],
                    self.d[VersionType.patch],
                )
            else:
                self.set_version(
                    self.d[VersionType.major],
                    self.d[VersionType.minor],
                    self.d[VersionType.patch] + 1,
                )

        else:
            current_type = self.current_special_type
            if current_type is None:
                self.d[VersionType.patch] += 1
                self.d[bump_type] = 1
            elif current_type is bump_type:
                self.d[bump_type] += 1
            elif bump_type.value > current_type.value:
                raise VersionError(
                    "Cannot bump from {} to {}",
                    current_type.name,
                    bump_type.name,
                )
            else:
                del self.d[current_type]
                self.d[bump_type] = 1
        logger.debug("Version bumped to {}", self)


class VersionManager:
    def __init__(self, path=None):
        if path is None:
            path = os.path.join(".", DEFAULT_METADATA_FILE)
        self.path = os.path.abspath(os.path.expanduser(path))

        VersionError.require_condition(
            os.path.exists(self.path),
            "Can't initialize VersionManager with nonextant path",
        )

        logger.debug("Reading version info from {}", self.path)
        if self.path.endswith(".json"):
            with open(self.path, "r") as json_file:
                self.metadata = json.load(json_file)
        else:
            self.metadata = pydon.load_file(self.path)
        self.version = Version()
        self.version.update_from_string(self.metadata["release"])
        logger.debug("Current version is {}", self.version)

        self.git_manager = GitManager(path=self.path)

        logger.debug("Initialized VersionManger for {}", self.path)

    def save_version(self):
        logger.debug("Saving current version to {}", self.path)
        self.metadata["release"] = repr(self.version)
        self.metadata["version"] = self.version.major_minor()
        if self.path.endswith(".json"):
            with open(self.path, "w") as json_file:
                json.dump(self.metadata, json_file, indent=4)
        else:
            pydon.dump_file(self.metadata, self.path, indent=4, width=1)
        logger.debug("Version saved")

    def tag_version(self, comment=None, bump_type=None):
        with DotException.handle_errors("Couldn't tag version"):
            logger.debug("Started tagging version")
            DotException.require_condition(
                self.git_manager.count_changes() == 0,
                "There must be no staged files before the tag can be made",
            )

            if bump_type is not None:

                self.version.bump(bump_type)

                self.save_version()
                self.git_manager.gitter.add(self.path)

                logger.debug("Attempting to edit changelog")
                top = self.git_manager.toplevel()
                changelog_files = [
                    os.path.join(top, f)
                    for f in os.listdir(top)
                    if re.search(r"(CHANGELOG|HISTORY|RELEASE|CHANGES)", f)
                ]
                if len(changelog_files) == 1:
                    changelog = changelog_files.pop()
                    os.system("$EDITOR {}".format(changelog))
                    self.git_manager.gitter.add(changelog)
                else:
                    logger.warning("Didn't find 1 changelog. Skipping edit")

                logger.debug("Commiting changes")
                self.git_manager.gitter.commit(
                    m="Version bumped to {}".format(self.version)
                )
                logger.debug("Pushing changes")
                self.git_manager.gitter.push()

            if comment is None:
                comment = "{name} version {release}"
            logger.debug("Formatting comment '{}' with metadata".format(comment))
            comment = comment.format(**self.metadata)

            logger.debug("Tag name (message) is '{}'".format(comment))

            logger.debug("Creating tag")
            self.git_manager.gitter.tag(
                str(self.version),
                annotate=True,
                message=comment,
            )

            logger.debug("Pushing tags")
            self.git_manager.gitter.push(tags=True)

            logger.debug("Finished tagging version")
