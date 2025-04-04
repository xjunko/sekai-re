"""sekai-re.py - project sekai file reverse engineering"""

import argparse
import json
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import UnityPy
import UnityPy.classes
import UnityPy.config
from PIL import Image

from lib import vgmstream

UnityPy.config.FALLBACK_UNITY_VERSION = "2022.3.21f1"


@dataclass
class Score:
    id: str
    difficulty: str
    data: str

    @classmethod
    def from_file(cls: "Score", score_path: Path) -> list["Score"]:
        score_fs = UnityPy.load(str(score_path.resolve()))
        scores: list["Score"] = []

        for obj in score_fs.objects:
            if obj.type.name == "TextAsset":
                score_id: str = score_path.name.split("_", 1)[0]
                score_object: UnityPy.classes.generated.TextAsset = obj.read()
                score_difficulty: str = score_object.m_Name
                score_data: str = score_object.m_Script
                scores.append(
                    cls(
                        id=score_id,
                        difficulty=score_difficulty,
                        data=score_data,
                    ),
                )

        return scores


@dataclass
class Track:
    id: str
    band: str
    data: bytes = field(default_factory=bytes)

    @classmethod
    def from_file(cls: "Track", track_path: Path) -> "Track":
        id: str = "01"
        band: str = "xx"

        if track_path.name[0].isdigit():
            id = track_path.name.split("_", 1)[0]
            band = "xx"
        else:
            id = track_path.name.split("_", 2)[2]
            band = track_path.name.split("_", 2)[0]

        audio_fs = UnityPy.load(str(track_path.resolve()))
        audio_found: bool = False
        for obj in audio_fs.objects:
            if obj.type.name == "TextAsset" and not audio_found:
                data: UnityPy.classes.generated.TextAsset = obj.read()
                mus_raw_data: bytes = data.m_Script.encode("utf-8", "surrogateescape")
                mus_data_converted: bytes = vgmstream.convert(mus_raw_data)
                return cls(
                    id=id,
                    band=band,
                    data=mus_data_converted,
                )


@dataclass
class Music:
    id: str
    jacket: Image.Image = field(default_factory=lambda: Image.new("RGB", (1, 1)))
    tracks: list[Track] = field(default_factory=list)
    scores: list[Score] = field(default_factory=list)


def load_musics(
    root_in: Path,
    root_out: Path,
    *,
    export: bool = True,
    clear_mem: bool = False,
) -> list[Music]:
    ids: set[str] = set()
    musics: list[Music] = []

    files: list[Path] = list((root_in / "music" / "long").glob("*"))
    score_files: list[Path] = list((root_in / "music" / "music_score").glob("*"))

    output_score: Path = root_out / "scores"
    if not output_score.exists():
        output_score.mkdir(parents=True, exist_ok=True)

    for audio_file in files:
        audio_id: str

        if audio_file.name[0].isdigit():  # No prefix, just the id
            audio_id = audio_file.name.split("_", 1)[0]
        else:  # Prefixed, usually band type
            audio_id = audio_file.name.split("_", 2)[1]

        if not audio_id.isdigit():
            continue

        if audio_id in ids:
            continue

        ids.add(audio_id)
        cur_mus: Music = Music(id=audio_id)

        # Load scores
        for score_file in (root_in / "music" / "music_score").glob(f"*"):
            if score_file.name.startswith(audio_id):
                mus_score: Score = Score.from_file(score_file)
                cur_mus.scores.extend(mus_score)

        # Load jacket
        jacket_file: Path = root_in / "music" / "jacket" / f"jacket_s_{audio_id[1:]}"

        if jacket_file.exists():
            jacket_fs = UnityPy.load(str(jacket_file.resolve()))
            jacket_found: bool = False
            for obj in jacket_fs.objects:
                if obj.type.name == "Texture2D" and not jacket_found:
                    data: UnityPy.classes.generated.Texture2D = obj.read()
                    cur_mus.jacket = data.image
                    jacket_found = True

        # Load audio
        cur_mus.tracks.append(Track.from_file(audio_file))

        # Load other audio version
        for audio_other in (root_in / "music" / "long").glob(f"*{audio_id}*"):
            if audio_file != audio_other:
                band_track: Track = Track.from_file(audio_other)
                cur_mus.tracks.append(band_track)

        if export:
            output_folder: Path = output_score / cur_mus.id
            if not output_folder.exists():
                output_folder.mkdir(parents=True, exist_ok=True)

            jacket_file = output_folder / "jacket.png"
            if not jacket_file.exists():
                cur_mus.jacket.save(jacket_file)

            for track in cur_mus.tracks:
                track_file = output_folder / f"audio_{track.band}_{track.id}.wav"
                if not track_file.exists():
                    track_file.write_bytes(track.data)

            for score in cur_mus.scores:
                score_file = output_folder / f"{score.difficulty}.sus"
                if not score_file.exists():
                    score_file.write_text(score.data)

        if clear_mem:
            for i in range(len(cur_mus.tracks)):
                cur_mus.tracks[i].data = b""
            for i in range(len(cur_mus.scores)):
                cur_mus.scores[i].data = ""
            cur_mus.jacket.close()

        musics.append(cur_mus)

        print(
            f"Progress: {len(musics)}/{len(score_files)} [{(len(musics) / len(score_files)) * 100.0:.02f}%]",
            end="\r",
        )

    return musics


def command_extract_music(args: argparse.Namespace) -> int:
    args = vars(args)

    # Start
    warnings.filterwarnings("ignore")
    root_in: Path = Path(args["in"].resolve())
    root_out: Path = Path(args["out"].resolve())

    musics: list[Music] = load_musics(root_in, root_out, export=True, clear_mem=True)

    data: dict[str, str] = {
        "name": "sekai-scores",
        "last_updated": time.time(),
        "musics": [],
    }

    musics.sort(key=lambda x: x.id)

    for music in musics:
        data["musics"].append(
            {
                "id": music.id,
                "jacket": music.jacket.size[0] != 1,
                "tracks": sorted(
                    [f"{track.band}_{track.id}" for track in music.tracks],
                ),
                "scores": sorted([score.difficulty for score in music.scores]),
            },
        )

    (root_out / "scores.json").write_text(json.dumps(data, indent=4))


def _main_argparse() -> int:
    parser = argparse.ArgumentParser(
        prog="sekai-re.py",
        description="Project Sekai reverse engineering suites",
        epilog="Currently only used for unpacking music assets",
    )

    # subparser
    subparser = parser.add_subparsers(dest="command", help="Subcommands")

    # supported action
    extract_music = subparser.add_parser(
        "extract_music",
        help="Decrypt and extract music assets",
    )
    extract_music.add_argument(
        "--in",
        type=Path,
        required=True,
        help="Root folder of the game assets",
    )
    extract_music.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Root folder to save the assets",
    )

    # parse args
    args = parser.parse_args()

    # handle
    if args.command == "extract_music":
        return command_extract_music(args)
    else:
        parser.print_help()
        return 1


def main() -> int:
    _main_argparse()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
