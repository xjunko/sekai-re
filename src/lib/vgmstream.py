"""vgmstream.py - a simple wrapper over the vgmstream-cli"""

import subprocess
import tempfile


def convert(data: bytes) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".acb") as file:
        file.write(data)
        file.flush()

        with tempfile.NamedTemporaryFile() as output_file:
            process = subprocess.Popen(
                [
                    "vgmstream-cli",
                    file.name,
                    "-p",
                ],
                stdout=subprocess.PIPE,
            )

            return process.stdout.read()
