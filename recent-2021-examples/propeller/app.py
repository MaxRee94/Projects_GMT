"""Main functionality for downloading and converting shots."""

import logging
import os
import pprint
import re
import subprocess
import time
from glob import glob
from pathlib import Path

import avalon.api
import avalon.io
import propeller.publish
import requests
import shotgun

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("propeller")


def main(
    episode,
    task,
    image_extension,
    audio_extension,
    process_single,
    image_quality,
    families,
    subset,
    app,
    dry_run=False,
):
    """Main function to run download, conversion and publish of shots of an
    episode directory.

    Args:
        episode(str):
            Episode name to download from.
        task(str):
            Task name to download from.
        image_extension(str):
            Output image extension.
        audio_extension(str):
            Output audio extension.
        process_single (bool):
            If True, only process the first shot. If False, process all shots.
        image_quality(str):
            Compression quality of output images.
        families(list):
            List of families to publish to.
        subset(str):
            Basename of subset to publish to.
        app(str):
            Name of (fake) app to publish from.
        dry_run(bool):
            If True, only show what would be done, without changing
            anything on the filesystem or the database."""

    representation_metadata = {
        "image_sequence": {
            "extension": image_extension,
            "ffmpeg_template": (
                "ffmpeg -y -i {infile} -f image2 -start_number 1001 "
                "-pix_fmt rgb24 -r {frame_rate} {outfile}"
                + (
                    " -qscale:v {}".format(image_quality)
                    if image_quality is not None
                    else ""
                )
                + " -loglevel 0"
            ),
            "path_pattern": ".{}$".format(image_extension),
            "path_replacement": "_%04d.{}".format(image_extension),
            "subdir": True,
        },
        "movie_file": {
            "extension": "mov",
        },
        "audio_file": {
            "extension": audio_extension,
            "ffmpeg_template": ("ffmpeg -y -i {infile} {outfile} -loglevel 0"),
        },
    }

    publisher = ShotgunToAvalonPublisher(
        episode,
        task,
        image_quality,
        subset,
        app,
        representation_metadata,
        families,
        process_single,
        dry_run,
    )
    global sg
    with shotgun.connect_shotgun(
        os.getenv("SG_SERVER_PATH"),
        script_name=os.getenv("SG_SCRIPT_NAME"),
        api_key=os.getenv("SG_SCRIPT_KEY"),
    ) as sg:
        publisher.process()

    print("")
    if not publisher.problems:
        logger.info(
            "Download, conversion and publish of {} for {} "
            "finished succesfully!\n".format(task, episode)
        )
    else:
        logger.debug(
            "Downloading, conversion, and/or publishing of {} "
            "for {} completed with problems:".format(task, episode)
        )
        pprint.pprint(publisher.problems, width=200)


def get_episode_dir(project_name, episode):
    """Get episode directory from project name and episode."""

    root = avalon.api.Session["AVALON_PROJECTS"]
    return "{}/{}/shots/{}".format(root, project_name, episode)


def get_project_filter(project_name):
    """Get project filter from project name."""

    sg_project = sg.find_one("Project", [["code", "is", project_name]])
    return ["project", "is", sg_project]


class ShotgunToAvalonPublisher:
    """Use this class to download, convert and
    publish an episode's shotgun footage.
    """

    additional_filter_presets = [
        {
            "preset_name": "LATEST",
            "latest_by": "ENTITIES_CREATED_AT",
        }
    ]
    maximum_process_count = int(os.environ["NUMBER_OF_PROCESSORS"]) / 2

    def __init__(
        self,
        episode,
        task,
        image_quality,
        subset_base,
        app,
        representation_metadata,
        families,
        process_single=True,
        dry_run=False,
    ):
        self.project = None
        self.episode = episode
        self.task = task
        self.process_single = process_single
        self.image_quality = image_quality
        self.processes = []
        self.subset_base = subset_base
        self.problems = []
        self.dry_run = dry_run
        self.representation_metadata = representation_metadata
        self.app = app
        self.families = families
        self.avalon_project = None
        self.file_template = None
        self.shots = {}
        self.episode_dir = None
        self.project_filter = None

    def process(self):
        """Download, convert and publish files."""

        self.install_avalon()
        self.collect_shot_data()
        self.publish_to_avalon()
        self.collect_publish_paths()
        self.download_episode()
        self.collect_framerates()
        self.create_conversion_commands()
        self.convert_shots()

    def collect_shot_data(self):
        """Collect shotgun versions for all shot directories in the
        episode directory."""

        shot_dirs = [
            path
            for path in glob("{}/*/*".format(self.episode_dir))
            if os.path.isdir(path)
        ]

        for shot_dir in shot_dirs:
            shot_code = os.path.basename(shot_dir)

            # Get sequence from shot code
            matches = re.findall("scn[0-9]+", shot_code)
            if matches:
                sequence = matches[0].replace("_", "")
            else:
                problem = "Sequence name could not be found. Skipped shot {}".format(
                    shot_code
                )
                logger.error(problem)
                self.problems.append(problem)
                continue

            # Get shot basename from shot code
            matches = re.findall("sh[0-9]+", shot_code)
            if matches:
                shot_basename = matches[0].replace("_", "")
            else:
                problem = "Shot basename could not be found. Skipped shot {}".format(
                    shot_code
                )
                logger.error(problem)
                self.problems.append(problem)
                continue

            self.shots[shot_code] = {
                "sequence": sequence,
                "shot_base": shot_basename,
            }

            if self.process_single:
                break

    def collect_publish_paths(self):
        """Collect publish filepaths and publish directories."""

        for shot_name, shot_data in self.shots.copy().items():
            for repr_name, repr_data in self.representation_metadata.items():
                if not shot_data[repr_name]["template_data"]:
                    problem = "Could not publish shot {}".format(shot_name)
                    logger.error(problem)
                    self.problems.append(problem)
                    del self.shots[shot_name]
                    break

                filepath = self.template.format(**shot_data[repr_name]["template_data"])

                if repr_data.get("subdir"):
                    filepath = os.path.join(filepath, os.path.basename(filepath))

                filepath = re.sub(
                    repr_data.get("path_pattern", ""),
                    repr_data.get("path_replacement", ""),
                    filepath,
                )

                self.shots[shot_name][repr_name]["path"] = os.path.normpath(filepath)

                publish_dir = str(Path(filepath).parent)
                if not os.path.exists(publish_dir):
                    os.makedirs(publish_dir)

            if self.shots.get(shot_name):
                self.shots[shot_name]["publish_dir"] = publish_dir

    def publish_to_avalon(self):
        """Publish all shots to avalon. This affects only the database, not
        the filesystem."""

        for shot_data in self.shots.values():
            version_up = True
            for repr_name, repr_data in self.representation_metadata.items():
                if self.dry_run:
                    continue

                template_data = propeller.publish.publish(
                    self.avalon_project,
                    self.task,
                    self.app,
                    self.families,
                    self.episode,
                    shot_data["sequence"],
                    shot_data["shot_base"],
                    self.subset_base,
                    repr_data["extension"],
                    version_up=version_up,
                    dry_run=self.dry_run,
                )
                version_up = False
                shot_data[repr_name] = {
                    "template_data": template_data,
                }

    def install_avalon(self):
        """Install avalon io and initialize avalon project, file template
        and episode directory."""

        avalon.io.install()
        self.project = avalon.api.Session["AVALON_PROJECT"]
        self.project_filter = get_project_filter(self.project)
        self.avalon_project = avalon.io.find_one({"type": "project"})
        self.template = self.avalon_project["config"]["template"]["publish"]
        self.episode_dir = get_episode_dir(self.project, self.episode)

    def get_filters(self, sg_shot):
        """Get project-, entity- and task filters."""

        filters = [
            self.project_filter,
            ["entity", "is", sg_shot],
            ["sg_task.Task.content", "is", self.task],
        ]

        return filters

    def get_versions(self, filters):
        """Get shotgun versions using filters.

        Args:
            filters(list): list of project-, entity- and task filters.
        """

        return sg.find(
            "Version",
            filters,
            ["sg_uploaded_movie"],
            additional_filter_presets=(self.additional_filter_presets),
        )

    def download_version(self, version, movie_path):
        """Download one version from shotgun.

        Args:
            version(dict):
                The shotgun version to be downloaded.
            movie_path(str):
                The destination path that the version "
                is to be downloaded to."""

        if self.dry_run:
            return True

        # Download from shotgun
        url = version["sg_uploaded_movie"]["url"]
        req = requests.get(url, allow_redirects=True)
        open(movie_path, "wb").write(req.content)

        # Check if download was successful
        if os.path.exists(movie_path) and os.path.getsize(movie_path) > 1000:
            logger.info(
                "Version {} downloaded successfully".format(
                    version["sg_uploaded_movie"]["name"]
                )
            )
            return True
        else:
            problem = "Version {} failed to download.".format(
                version["sg_uploaded_movie"]["name"]
            )
            logger.error(problem)
            self.problems.append(problem)

    def collect_framerates(self):
        """Collect and store frame rate of each downloaded video."""

        logger.info("Collecting framerates for {}...".format(self.episode))

        for shot_code, shot_data in self.shots.copy().items():
            framerate_probe_cmd = [
                "ffprobe",
                "-v",
                "0",
                "-of",
                "csv=p=0",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=r_frame_rate",
                shot_data["movie_file"]["path"],
            ]
            process = subprocess.Popen(framerate_probe_cmd, stdout=subprocess.PIPE)
            output = process.communicate()[0]

            # parse output string
            framerate_string = re.sub(r"b'|\\r\\n'", "", str(output))

            # calculate framerate
            framerate = framerate_string.split("/")
            try:
                framerate = float(framerate[0]) / float(framerate[1])
                self.shots[shot_code]["frame_rate"] = framerate
            except ValueError:
                problem = "Could not find a framerate for shot {}".format(shot_code)
                self.problems.append(problem)
                logger.error(problem)
                del self.shots[shot_code]

        logger.info("Collected framerates for {}".format(self.episode))

    def update_running_processes(self):
        """Stop tracking threads and processes that are no longer running."""

        for process in self.processes:
            if hasattr(process, "poll"):
                if process.poll() is not None:
                    self.processes.remove(process)
            elif hasattr(process, "is_alive"):
                if not process.is_alive():
                    self.processes.remove(process)

    def get_filesequence_firstframe(self, filesequence_path, extension):
        """Return first frame of image sequence."""

        return re.sub(
            "_%04d.{}$".format(extension),
            "_1001.{}".format(extension),
            filesequence_path,
        )

    def convert_shots(self):
        """Run conversion commands for all downloaded movie files."""

        # Start conversion processes
        for shot_code, shot_data in self.shots.items():
            ffmpeg_commands = shot_data["ffmpeg_commands"]

            i = 0
            while i < (len(ffmpeg_commands)):
                self.update_running_processes()

                # Start conversion process if the amount of active
                # processes is below the defined limit.
                if len(self.processes) < self.maximum_process_count:
                    ffmpeg_command = ffmpeg_commands[i]
                    logger.info(" ".join(ffmpeg_command))
                    if not self.dry_run:
                        process = subprocess.Popen(
                            ffmpeg_command, stdout=subprocess.PIPE
                        )
                        self.processes.append(process)
                    i += 1
                else:
                    time.sleep(0.2)

        # Wait until all processes have finished
        logger.info("Waiting for conversion processes to finish...")
        while True:
            _old_processes = self.processes.copy()
            self.update_running_processes()
            if not self.processes:
                logger.info("All conversion processes have finished.\n")
                break
            elif len(self.processes) < len(_old_processes):
                logger.info(
                    "   - Active conversion "
                    "processes: {}".format(len(self.processes))
                )

        # Check if all shots have been converted correctly
        logger.info("Checking conversion success...")
        for shot_code, shot_data in self.shots.items():
            filesequence_firstframe = self.get_filesequence_firstframe(
                shot_data["image_sequence"]["path"],
                self.representation_metadata["image_sequence"]["extension"],
            )

            problem = None
            if not os.path.exists(filesequence_firstframe):
                problem = "Imagesequence-creation failed for shot: {}".format(shot_code)
                logger.error(problem)
                self.problems.append(problem)

            if not os.path.exists(shot_data["audio_file"]["path"]):
                problem = "Audiofile-creation failed for shot: {}".format(shot_code)
                logger.error(problem)
                self.problems.append(problem)

            if not problem:
                logger.info("Succesfully converted shot {}.".format(shot_code))

    def create_conversion_commands(self):
        """Create ffmpeg conversion commands for non-moviefile representations."""

        for shot in self.shots.values():
            shot["ffmpeg_commands"] = []
            for repr_name, repr_data in self.representation_metadata.items():
                ffmpeg_template = repr_data.get("ffmpeg_template")
                if ffmpeg_template:
                    ffmpeg_data = {
                        "infile": shot["movie_file"]["path"],
                        "outfile": shot[repr_name]["path"],
                    }
                    if repr_name == "image_sequence":
                        ffmpeg_data["frame_rate"] = shot["frame_rate"]

                    ffmpeg_string = ffmpeg_template.format(**ffmpeg_data)
                    ffmpeg_command = ffmpeg_string.split(" ")
                    shot["ffmpeg_commands"].append(ffmpeg_command)

    def download_episode(self):
        """Download all shot versions of an episode from shotgun."""

        logger.info("Starting download...")
        for shot_code, shot_data in self.shots.copy().items():
            sg_shot = sg.find_one(
                "Shot",
                [
                    self.project_filter,
                    ["code", "is", shot_code],
                ],
            )
            filters = self.get_filters(sg_shot)

            # Get version shotgun data
            versions = self.get_versions(filters)
            if versions:
                version = versions[0]
            else:
                problem = "No versions found for shot directory {}".format(shot_code)
                logger.error(problem)
                self.problems.append(problem)
                continue

            shot_data["version"] = version
            self.shots[shot_code] = shot_data

            # Download version
            success = False
            if not self.dry_run:
                success = self.download_version(
                    shot_data["version"],
                    shot_data["movie_file"]["path"],
                )

            if not success:
                del self.shots[shot_code]

            if self.process_single:
                break

        logger.info("Finished {} download.\n".format(self.episode))
