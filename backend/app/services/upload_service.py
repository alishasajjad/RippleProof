from __future__ import annotations

import io
import os
import re

from dataclasses import (
    dataclass,
)

from pathlib import (
    Path,
)

from fastapi import (
    UploadFile,
)

from pypdf import (
    PdfReader,
)

from app.schemas.contracts import (
    Artifact,
)


MAX_FILE_SIZE = int(
    os.getenv(
        "MAX_UPLOAD_FILE_BYTES",
        str(
            2
            * 1024
            * 1024
        ),
    )
)

MAX_TOTAL_UPLOAD_SIZE = int(
    os.getenv(
        "MAX_TOTAL_UPLOAD_BYTES",
        str(
            10
            * 1024
            * 1024
        ),
    )
)

MAX_UPLOAD_FILES = int(
    os.getenv(
        "MAX_UPLOAD_FILES",
        "10",
    )
)

MAX_PDF_PAGES = 30

MAX_EXTRACTED_CHARS = 120_000


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".json",
    ".yaml",
    ".yml",
    ".csv",
    ".pdf",
}


@dataclass
class ParsedUpload:
    artifact: Artifact
    size_bytes: int


class UploadService:

    async def parse_files(
        self,
        files: list[
            UploadFile
        ],
    ) -> list[
        Artifact
    ]:

        if not files:

            raise ValueError(
                "At least one artifact "
                "must be uploaded."
            )


        if (
            len(files)
            > MAX_UPLOAD_FILES
        ):

            raise ValueError(
                f"Maximum "
                f"{MAX_UPLOAD_FILES} "
                f"files are allowed."
            )


        artifacts: list[
            Artifact
        ] = []

        used_ids: set[
            str
        ] = set()

        total_size = 0


        for index, file in enumerate(
            files
        ):

            parsed = await (
                self._parse_one(
                    file=file,
                    index=index,
                    used_ids=used_ids,
                )
            )

            total_size += (
                parsed.size_bytes
            )


            if (
                total_size
                > MAX_TOTAL_UPLOAD_SIZE
            ):

                raise ValueError(
                    "Combined upload exceeds "
                    "the 10 MB MVP limit."
                )


            artifacts.append(
                parsed.artifact
            )


        return artifacts


    async def _parse_one(
        self,
        file: UploadFile,
        index: int,
        used_ids: set[str],
    ) -> ParsedUpload:

        original_filename = (
            file.filename
            or
            f"artifact-{index + 1}.txt"
        )


        filename = (
            Path(
                original_filename
            )
            .name
        )


        extension = (
            Path(
                filename
            )
            .suffix
            .lower()
        )


        if (
            extension
            not in
            SUPPORTED_EXTENSIONS
        ):

            raise ValueError(
                f"Unsupported file type "
                f"'{extension or 'unknown'}' "
                f"for {filename}."
            )


        raw = await file.read()


        if not raw:

            raise ValueError(
                f"{filename} is empty."
            )


        if (
            len(raw)
            > MAX_FILE_SIZE
        ):

            raise ValueError(
                f"{filename} exceeds "
                f"the 2 MB file limit."
            )


        if (
            extension
            == ".pdf"
        ):

            content = (
                self._read_pdf(
                    raw,
                    filename,
                )
            )

        else:

            content = (
                self._decode_text(
                    raw
                )
            )


        content = (
            content
            .replace(
                "\x00",
                ""
            )
            .strip()
        )


        if (
            len(content)
            > MAX_EXTRACTED_CHARS
        ):

            content = (
                content[
                    :MAX_EXTRACTED_CHARS
                ]
            )


        if not content:

            raise ValueError(
                f"No readable text "
                f"found in {filename}."
            )


        artifact_type = (
            self._infer_artifact_type(
                filename,
                extension,
                content,
            )
        )


        relationship = (
            self._default_relationship(
                artifact_type
            )
        )


        artifact_id = (
            self._unique_id(
                filename,
                index,
                used_ids,
            )
        )


        return ParsedUpload(
            artifact=Artifact(
                id=artifact_id,
                name=filename,
                artifact_type=(
                    artifact_type
                ),
                content=content,
                relationship=(
                    relationship
                ),
                source_path=(
                    filename
                ),
            ),

            size_bytes=len(
                raw
            ),
        )


    @staticmethod
    def _decode_text(
        raw: bytes,
    ) -> str:

        for encoding in [
            "utf-8",
            "utf-8-sig",
            "cp1252",
            "latin-1",
        ]:

            try:

                return raw.decode(
                    encoding
                )

            except UnicodeDecodeError:
                continue


        raise ValueError(
            "Could not decode "
            "uploaded text file."
        )


    @staticmethod
    def _read_pdf(
        raw: bytes,
        filename: str,
    ) -> str:

        try:

            reader = PdfReader(
                io.BytesIO(
                    raw
                )
            )


            if (
                len(
                    reader.pages
                )
                > MAX_PDF_PAGES
            ):

                raise ValueError(
                    f"{filename} exceeds "
                    f"the {MAX_PDF_PAGES}-page "
                    f"PDF limit."
                )


            pages: list[
                str
            ] = []


            for page in (
                reader.pages
            ):

                text = (
                    page.extract_text()
                    or ""
                )


                if text.strip():

                    pages.append(
                        text
                    )


            return "\n\n".join(
                pages
            )


        except ValueError:
            raise


        except Exception as exc:

            raise ValueError(
                f"Could not read PDF "
                f"{filename}."
            ) from exc


    @staticmethod
    def _infer_artifact_type(
        filename: str,
        extension: str,
        content: str,
    ) -> str:

        lower_name = (
            filename.lower()
        )

        lower_content = (
            content.lower()
        )


        code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
        }


        if (
            extension
            in code_extensions
        ):

            if any(
                token in lower_name
                for token in [
                    "api",
                    "route",
                    "controller",
                    "service",
                    "endpoint",
                ]
            ):

                return "API"


            return "CODE"


        if any(
            token in lower_name
            for token in [
                "chatbot",
                "bot",
                "assistant",
                "prompt",
            ]
        ):

            return "CHATBOT"


        if any(
            token in lower_name
            for token in [
                "form",
                "application",
                "request_form",
            ]
        ):

            return "FORM"


        if any(
            token in lower_name
            for token in [
                "faq",
                "website",
                "web",
                "help",
            ]
        ):

            return "WEBSITE"


        if (
            extension
            == ".html"
        ):

            return "WEBSITE"


        if (
            "fastapi"
            in lower_content
            or
            "@app."
            in lower_content
            or
            "@router."
            in lower_content
        ):

            return "API"


        return "DOCUMENT"


    @staticmethod
    def _default_relationship(
        artifact_type: str,
    ) -> str:

        mapping = {
            "API":
                "ENFORCES",

            "CODE":
                "ENFORCES",

            "FORM":
                "DEPENDS_ON",

            "CHATBOT":
                "DESCRIBES",

            "WEBSITE":
                "DESCRIBES",

            "DOCUMENT":
                "REFERENCES",
        }


        return mapping.get(
            artifact_type,
            "REFERENCES",
        )


    @staticmethod
    def _unique_id(
        filename: str,
        index: int,
        used_ids: set[str],
    ) -> str:

        stem = (
            Path(
                filename
            )
            .stem
            .lower()
        )


        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            stem,
        ).strip(
            "-"
        )


        if not slug:

            slug = (
                f"artifact-"
                f"{index + 1}"
            )


        candidate = slug

        counter = 2


        while (
            candidate
            in used_ids
        ):

            candidate = (
                f"{slug}-"
                f"{counter}"
            )

            counter += 1


        used_ids.add(
            candidate
        )


        return candidate