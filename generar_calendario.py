#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TARGETS = ("bilbao", "bilbo", "basauri")
URL_TEMPLATE = (
    "https://opendata.euskadi.eus/contenidos/ds_eventos/"
    "calendario_laboral_{year}/opendata/calendario_laboral_{year}.ics"
)


def unfold_ics(text: str) -> str:
    return re.sub(r"\r?\n[ \t]", "", text)


def escape_ics(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace("\n", r"\n")
    )


def parse_events(text: str) -> list[str]:
    return re.findall(
        r"BEGIN:VEVENT\r?\n.*?END:VEVENT",
        unfold_ics(text),
        flags=re.S | re.I,
    )


def property_value(event: str, name: str) -> str:
    match = re.search(
        rf"^{re.escape(name)}(?:;[^:]*)?:(.*)$",
        event,
        flags=re.M | re.I,
    )
    return match.group(1).strip() if match else ""


def applies_to_targets(event: str) -> bool:
    haystack = event.casefold()
    return any(target in haystack for target in TARGETS)


def event_key(event: str) -> tuple[str, str]:
    return (
        property_value(event, "DTSTART"),
        property_value(event, "SUMMARY").casefold(),
    )


def stable_uid(event: str) -> str:
    digest = hashlib.sha256(repr(event_key(event)).encode("utf-8")).hexdigest()[:20]
    return f"{digest}@festivos-bilbao-basauri"


def clean_event(event: str) -> str:
    lines = event.splitlines()
    result: list[str] = []
    uid_replaced = False
    for line in lines:
        if line.upper().startswith("UID:"):
            result.append(f"UID:{stable_uid(event)}")
            uid_replaced = True
        else:
            result.append(line)
    if not uid_replaced:
        result.insert(1, f"UID:{stable_uid(event)}")
    return "\r\n".join(result)


def download_year(year: int) -> str:
    url = URL_TEMPLATE.format(year=year)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "festivos-bilbao-basauri/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8-sig")


def build_calendar(years: list[int]) -> str:
    selected: dict[tuple[str, str], str] = {}
    downloaded = 0

    for year in years:
        try:
            source = download_year(year)
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            print(f"Aviso: no se pudo descargar {year}: {exc}")
            continue

        matches = [event for event in parse_events(source) if applies_to_targets(event)]
        if not matches:
            print(f"Aviso: no se encontraron eventos para Bilbao/Basauri en {year}")
            continue

        downloaded += 1
        for event in matches:
            selected.setdefault(event_key(event), clean_event(event))

    if downloaded == 0 or not selected:
        raise RuntimeError("No se pudo generar el calendario con ninguno de los años solicitados")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    header = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AsierB//Festivos Bilbao y Basauri//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Festivos Bilbao y Basauri",
        "X-WR-TIMEZONE:Europe/Madrid",
        f"X-WR-CALDESC:{escape_ics('Calendario filtrado desde Open Data Euskadi. Actualizado ' + stamp)}",
    ]
    body = [selected[key] for key in sorted(selected)]
    return "\r\n".join(header + body + ["END:VCALENDAR", ""])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    calendar = build_calendar(args.years)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(calendar, encoding="utf-8", newline="")
    print(f"Creado {args.output} con {calendar.count('BEGIN:VEVENT')} eventos")


if __name__ == "__main__":
    main()
