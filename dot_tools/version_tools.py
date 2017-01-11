import enum
import bidict
import re
import json
import os
import logging

from dot_tools.misc_tools import DotException
from dot_tools.git_tools import GitManager


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
        return (cls.short_dict().get(key) or getattr(cls, key))


class Version:

    def __init__(self, *args, **kwargs):
        self.set_version(*args, **kwargs)

    @classmethod
    def from_string(cls, text):
        match = re.match(
            r'^v?(\d+)\.(\d+)\.(\d+)(?:-(\w+)(\d+))?$',
            text,
        )
        VersionError.require_condition(
            match is not None,
            "Couldn't parse version",
        )
        return cls(*match.groups())

    def __repr__(self):
        text = '{}.{}.{}'.format(
            self.d[VersionType.major],
            self.d[VersionType.minor],
            self.d[VersionType.patch],
        )
        if self.current_special_type is not None:
            text = '{}-{}{}'.format(
                text,
                VersionType.short_dict().inv[self.current_special_type],
                self.d[self.current_special_type],
            )
        return text

    def __str__(self):
        return 'v' + repr(self)

    def major_minor(self):
        return '{}.{}'.format(
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
        self, major_num, minor_num, patch_num,
        extra_type=None, extra_num=None
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
        if not isinstance(bump_type, VersionType):
            bump_type = VersionType.lookup(bump_type)

        if bump_type is VersionType.major:
            self.set_version(self.d[VersionType.major] + 1, 0, 0)

        elif bump_type is VersionType.minor:
            self.set_version(
                self.d[VersionType.major],
                self.d[VersionType.minor] + 1,
                0
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


def get_current_version(path=None, metadata=None):
    if metadata is None:
        with open(path, 'r') as metadata_file:
            metadata = json.load(metadata_file)
    return Version.from_string(metadata['release'])


def tag_version(
        git_manager=None, logger=None,
        comment=None, bump_type=None, path=None,
):
    if logger is None:
        logger = logging.getLogger(__name__)
    if git_manager is None:
        git_manager = GitManager(logger=logger)

    with DotException.handle_errors("Couldn't tag version"):
        logger.debug("Started tagging version")

        logger.debug("Reading metadata file: {}".format(path))
        with open(path, 'r') as metadata_file:
            metadata = json.load(metadata_file)

        logger.debug("Extracting version from metadata")
        version = get_current_version(path, metadata=metadata)
        logger.debug("Extracted version as: {}".format(version))

        if bump_type is not None:
            version.bump(bump_type)
            logger.debug("Version bumped to: {}".format(version))
            metadata['release'] = repr(version)
            metadata['version'] = version.major_minor()
            with open(path, 'w') as metadata_file:
                json.dump(metadata, metadata_file, sort_keys=True, indent=4)

            DotException.require_condition(
                git_manager.count_changes() == 0,
                "There must be no staged files before the tag can be made",
            )

            logger.debug("Attempting to edit changelog")
            top = git_manager.toplevel()
            changelog_files = [
                os.path.join(top, f)
                for f in os.listdir(top)
                if re.search(r'(CHANGELOG|HISTORY|RELEASE|CHANGES)', f)
            ]
            if len(changelog_files) == 1:
                changelog = changelog_files.pop()
                os.system('$EDITOR {}'.format(changelog))
                git_manager.gitter.add(changelog)
            else:
                logger.warning("Didn't find 1 changelog. Skipping edit")

            logger.debug("Adding {} for commit".format(path))
            git_manager.gitter.add(path)
            logger.debug("Commiting changes")
            git_manager.gitter.commit(m="Version bumped to {}".format(version))
            logger.debug("Pushing changes")
            git_manager.gitter.push()

        logger.debug("Formatting comment '{}' with metadata".format(comment))
        if comment is None:
            comment = "{name} version {release}"
        comment = comment.format(**metadata)
        logger.debug("Formatted comment is '{}'".format(comment))

        logger.debug("Creating tag")
        git_manager.gitter.tag(
            "'{}'".format(str(version)),
            annotate=True,
            message="'{}'".format(comment),
        )

        logger.debug("Pushing tags")
        git_manager.gitter.push(tags=True)

        logger.debug("Finished tagging version")
