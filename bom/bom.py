#!/usr/bin/env python3
# ================================
# Name: 'a-hardware-template'/bom/bom.py
# Source: https://github.com/a-mcorp/a-hardware-template
# SPDX-License-Identifier: MIT-0
# Year: 2026
# ================================

"""Bill of materials for '{project-name}': totals, and bom/BOM.md with the part dimensions.

Usage:
    python3 bom/bom.py                 # report in the base currency of rates.csv (first row, EUR by default)
    python3 bom/bom.py --currency PLN  # report in another currency from rates.csv

bom.csv columns:
    id, part, category (shipping rows are summed into one row at the bottom), manufacturer,
    mpn (the maker's part number, optional), supplier, sku (the supplier's code, optional) - together the Code column,
    qty (a number, or text such as "1 + 1" - then the price is for all of them), unit_price,
    unit_price_max (optional, for estimates), currency,
    origin (ordered | planned | printed | at hand | cancelled - at hand parts are already owned:
    their price is a reference, not spent; cancelled rows are left out),
    small (yes - a small part: listed under Small Parts, without cost),
    optional (yes - listed with its cost, but not counted in the totals), order_date, notes

rates.csv: currency, rate - the value of 1 unit of that currency in the base currency.
The Total table shows the report currency and every other currency paid in bom.csv.

dimensions.csv columns (optional file, in mm; each row goes into one table or both):
    id (as in bom.csv), part (optional - overrides the name from bom.csv),
    Dimensions table - outline (the part's size, on its first row), details,
    used (measured | drawing | estimate - where the CAD value comes from),
    source (datasheet | listing - for used = drawing), source_url (link to the maker's datasheet - never commit the file itself;
    shop listings are named, not linked),
    source_notes (added after the source, e.g. "PCB measured");
    Dimensions Validation table - feature, maker (the maker's value), measured (calipers),
    verdict (matches | inaccurate | missing | no drawing | to measure), verdict_notes, checked (date)
"""

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

Row = dict[str, str]

DIRECTORY_BOM: Path = Path(__file__).resolve().parent
CSV_BOM: Path = DIRECTORY_BOM / "bom.csv"
CSV_RATES: Path = DIRECTORY_BOM / "rates.csv"
CSV_DIMENSIONS: Path = DIRECTORY_BOM / "dimensions.csv"
MD_BOM: Path = DIRECTORY_BOM / "BOM.md"

VALUES_ORIGIN: tuple[str, ...] = ("ordered", "planned", "printed", "at hand", "cancelled")
VALUES_USED: tuple[str, ...] = ("measured", "drawing", "estimate", "")
VALUES_SOURCE: tuple[str, ...] = ("datasheet", "listing", "")
VALUES_VERDICT: tuple[str, ...] = ("matches", "inaccurate", "missing", "no drawing", "to measure", "")
ORDER_ORIGIN: dict[str, int] = {origin: index for index, origin in enumerate(VALUES_ORIGIN)}


def csv_read(path: Path) -> list[Row]:
    with path.open(newline="", encoding="utf-8") as file:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(file)]


def csv_values_check(path: Path, rows: list[Row], column: str, values_allowed: tuple[str, ...]) -> None:
    for line, row in enumerate(rows, start=2):
        if row[column] not in values_allowed:
            names_allowed = ", ".join(value or "(empty)" for value in values_allowed)
            sys.exit(f"{path.name}, line {line}: unknown value in '{column}': '{row[column]}' (use one of {names_allowed})")


def csv_rates_load(path: Path) -> tuple[str, dict[str, float]]:
    """Return the base currency (first row) and the rates to it."""
    rows = csv_read(path)
    if not rows:
        sys.exit(f"{path.name}: no rates")
    rates = {row["currency"].upper(): float(row["rate"]) for row in rows}
    return rows[0]["currency"].upper(), rates


def csv_bom_load(path: Path) -> list[Row]:
    rows = csv_read(path)
    csv_values_check(path, rows, "origin", VALUES_ORIGIN)
    return rows


def csv_dimensions_load(path: Path) -> list[Row]:
    if not path.exists():
        return []
    rows = csv_read(path)
    csv_values_check(path, rows, "used", VALUES_USED)
    csv_values_check(path, rows, "source", VALUES_SOURCE)
    csv_values_check(path, rows, "verdict", VALUES_VERDICT)
    return rows


def flag_yes_check(value: str) -> bool:
    return value.lower() == "yes"


def qty_number_parse(row: Row) -> float:
    """A numeric qty multiplies the price; text ("1 + 1", "-") means the price is for all of them."""
    try:
        return float(row["qty"] or 1)
    except ValueError:
        return 1.0


def currency_convert(value: float, currency: str, currency_target: str, rates: dict[str, float]) -> float:
    for currency_checked in (currency, currency_target):
        if currency_checked not in rates:
            sys.exit(f"rates.csv: no rate for {currency_checked}")
    return value * rates[currency] / rates[currency_target]


def row_cost_calculate(row: Row, currency_target: str, rates: dict[str, float]) -> tuple[float, float]:
    """Return the (low, high) total cost of a row in the target currency."""
    qty = qty_number_parse(row)
    price_low = float(row["unit_price"] or 0)
    price_high = float(row["unit_price_max"] or price_low)
    currency = row["currency"].upper()
    return (
        currency_convert(qty * price_low, currency, currency_target, rates),
        currency_convert(qty * price_high, currency, currency_target, rates),
    )


def money_format(cost_low: float, cost_high: float) -> str:
    return f"{cost_low:.2f}" if abs(cost_high - cost_low) < 0.005 else f"{cost_low:.2f}–{cost_high:.2f}"


def money_approx_format(cost_low: float, cost_high: float) -> str:
    return f"≈ {money_format(cost_low, cost_high)}"


def cell_code_format(row: Row) -> str:
    """The maker's part number, then the shop's code as 'shop: code'."""
    code_shop = f"{row['supplier']}: {row['sku']}" if row["supplier"] else row["sku"]
    if row["mpn"] and row["sku"]:
        return f"{row['mpn']}, {code_shop}"
    if row["mpn"]:
        return row["mpn"]
    if row["sku"]:
        return code_shop
    return "-"


def cell_name_format(row: Row) -> str:
    return row["part"]


def cell_paid_format(row: Row) -> str:
    if row["origin"] != "ordered" or not row["unit_price"]:
        return "-"
    return f"{float(row['unit_price']) * qty_number_parse(row):.2f} {row['currency'].upper()}"


def cell_qty_format(row: Row) -> str:
    return row["qty"] or "1"


class Sums:
    """Low and high sums per origin, in one currency."""

    def __init__(self) -> None:
        self.sums_origin: dict[str, list[float]] = {origin: [0.0, 0.0] for origin in VALUES_ORIGIN}

    def sum_add(self, origin: str, cost_low: float, cost_high: float) -> None:
        self.sums_origin[origin][0] += cost_low
        self.sums_origin[origin][1] += cost_high

    def sum_get(self, *origins: str) -> tuple[float, float]:
        return (
            sum(self.sums_origin[origin][0] for origin in origins),
            sum(self.sums_origin[origin][1] for origin in origins),
        )


def table_parts_build(rows_parts: list[Row], rows_shipping: list[Row], currency_target: str, rates: dict[str, float]) -> list[str]:
    lines = [
        f"| Part | [Code](#legend) | [Origin](#legend) | Supplier | Qty | Notes | [Paid](#legend) | [Cost ({currency_target})](#legend) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in sorted(rows_parts, key=lambda row: ORDER_ORIGIN[row["origin"]]):
        cost_low, cost_high = row_cost_calculate(row, currency_target, rates)
        if not cost_high:
            cost = "-"
        elif row["origin"] == "ordered":
            cost = money_format(cost_low, cost_high)
        else:
            cost = money_approx_format(cost_low, cost_high)
        notes = row["notes"]
        if flag_yes_check(row["optional"]):
            notes = "optional, not counted" + (f" - {notes}" if notes else "")
        lines.append(f"| {cell_name_format(row)} | {cell_code_format(row)} | {row['origin']} | {row['supplier'] or '-'} | {cell_qty_format(row)} | {notes} | {cell_paid_format(row)} | {cost} |")
    if rows_shipping:
        # one row for all shipping: an estimate, as it varies per order, summed per supplier
        costs_supplier: dict[str, list[float]] = {}
        paid_currency: dict[str, float] = {}
        cost_low_sum = cost_high_sum = 0.0
        for row in rows_shipping:
            cost_low, cost_high = row_cost_calculate(row, currency_target, rates)
            cost_low_sum += cost_low
            cost_high_sum += cost_high
            supplier = row["supplier"] or "-"
            costs_supplier.setdefault(supplier, [0.0, 0.0])
            costs_supplier[supplier][0] += cost_low
            costs_supplier[supplier][1] += cost_high
            if row["origin"] == "ordered" and row["unit_price"]:
                currency = row["currency"].upper()
                paid_currency[currency] = paid_currency.get(currency, 0.0) + float(row["unit_price"]) * qty_number_parse(row)
        suppliers = ", ".join(f'"{supplier}"' for supplier in costs_supplier)
        notes = "varies per order: " + ", ".join(
            f'"{supplier}" {money_approx_format(*costs)} {currency_target}' for supplier, costs in costs_supplier.items()
        )
        paid = ", ".join(f"{value:.2f} {currency}" for currency, value in paid_currency.items()) or "-"
        lines.append(f"| Shipping | - | ordered | {suppliers} | - | {notes} | {paid} | {money_approx_format(cost_low_sum, cost_high_sum)} |")
    return lines


def table_small_build(rows_small: list[Row]) -> list[str]:
    lines = ["| Part | [Code](#legend) | [Origin](#legend) | Supplier | Qty | Where |", "|---|---|---|---|---|---|"]
    for row in sorted(rows_small, key=lambda row: ORDER_ORIGIN[row["origin"]]):
        lines.append(f"| {cell_name_format(row)} | {cell_code_format(row)} | {row['origin']} | {row['supplier'] or '-'} | {cell_qty_format(row)} | {row['notes']} |")
    return lines


def cell_source_format(dimension: Row, link: bool) -> str:
    """measured - the Operator's calipers; datasheet or listing - linked; estimate - to measure."""
    if dimension["used"] in ("measured", "estimate", ""):
        label = dimension["used"]
    else:
        label = dimension["source"] or "datasheet"
        if link and label == "datasheet" and dimension["source_url"].startswith("http"):
            label = f"[{label}]({dimension['source_url']})"
    if link and dimension["source_notes"]:
        label = f"{label}; {dimension['source_notes']}" if label else dimension["source_notes"]
    return label or "-"


def cell_part_format(dimension: Row, names: dict[str, str]) -> str:
    return dimension["part"] or names.get(dimension["id"], dimension["id"])


def table_dimensions_build(dimensions: list[Row], names: dict[str, str]) -> list[str]:
    """The values the CAD uses, per part: the outline, then the details."""
    lines = ["| Part | Outline | Details | [Source](#legend) |", "|---|---|---|---|"]
    part_last = None
    for dimension in dimensions:
        if not (dimension["outline"] or dimension["details"]):
            continue
        part = cell_part_format(dimension, names)
        part_shown, part_last = ("" if part == part_last else part), part
        lines.append(f"| {part_shown} | {dimension['outline']} | {dimension['details']} | {cell_source_format(dimension, link=True)} |")
    return lines


def table_validation_build(dimensions: list[Row], names: dict[str, str]) -> list[str]:
    """Which value the CAD uses, and why."""
    lines = ["| Part | Value | Maker | Measured | [Verdict](#legend) | Notes |", "|---|---|---|---|---|---|"]
    part_last = None
    for dimension in dimensions:
        if not dimension["verdict"]:
            continue
        part = cell_part_format(dimension, names)
        part_shown, part_last = ("" if part == part_last else part), part
        maker = dimension["maker"]
        if dimension["source"] == "listing" and maker:
            maker = f"{maker} (listing)"
        verdict = f"{dimension['verdict']} → {cell_source_format(dimension, link=False)}"
        lines.append(f"| {part_shown} | {dimension['feature']} | {maker or '-'} | {dimension['measured'] or '-'} | {verdict} | {dimension['verdict_notes']} |")
    return lines


LEGEND_PARTS: list[tuple[str, str]] = [
    ("Code", "The maker's part number, then the shop's code as 'shop: code'."),
    ("Origin", "Where the part comes from: *ordered* - bought for this project; *planned* - still to buy, the cost is an "
     "estimate; *printed* - made on the printer, its cost is in the filament; *at hand* - already owned, with a generic "
     "reference price for anyone rebuilding the device, not counted as spent."),
    ("Paid", "The amount as paid, in the shop's currency, VAT included."),
]
LEGEND_SOURCE: tuple[str, str] = (
    "Source", "Where the value comes from: *datasheet* - the maker's datasheet or mechanical drawing, linked where it is "
    "published online (never stored here); *listing* - the shop's product page; *measured* - measured by hand with "
    "calipers; *estimate* - a guess, to be measured (marked `MEASURE` in the CAD).")
LEGEND_VERDICT: tuple[str, str] = (
    "Verdict", "How the makers' value compares with the measurement, then which one the CAD uses: *matches* - the two "
    "agree within the clearance; *inaccurate* - the maker's value is off (generic listings, slanted or hand-soldered "
    "parts, pouch tolerance), so the caliper measurement is used; *missing* - the maker gives no value, so it is "
    "measured; *no drawing* - the maker publishes no drawing at all; *to measure* - not measured yet, the maker's value "
    "is used for now.")


def bom_generate() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--currency", help="report currency (default: the first row of rates.csv)")
    arguments = parser.parse_args()

    currency_base, rates = csv_rates_load(CSV_RATES)
    currency_target: str = (arguments.currency or currency_base).upper()
    rows_bom: list[Row] = csv_bom_load(CSV_BOM)
    rows_active: list[Row] = [row for row in rows_bom if row["origin"] != "cancelled"]
    rows_small: list[Row] = [row for row in rows_active if flag_yes_check(row["small"])]
    rows_counted: list[Row] = [row for row in rows_active if not flag_yes_check(row["small"])]
    rows_shipping: list[Row] = [row for row in rows_counted if row["category"] == "shipping"]
    rows_parts: list[Row] = [row for row in rows_counted if row["category"] != "shipping"]

    currencies: list[str] = [currency_target] + sorted({row["currency"].upper() for row in rows_active} - {currency_target})
    sums_currency: dict[str, Sums] = {currency: Sums() for currency in currencies}
    for row in rows_counted:
        if flag_yes_check(row["optional"]):
            continue
        for currency in currencies:
            sums_currency[currency].sum_add(row["origin"], *row_cost_calculate(row, currency, rates))

    dimensions: list[Row] = csv_dimensions_load(CSV_DIMENSIONS)
    names: dict[str, str] = {row["id"]: row["part"] for row in rows_bom}

    currencies_other: list[str] = currencies[1:]
    rates_shown = ", ".join(f"1 {currency} = {currency_convert(1, currency, currency_target, rates):.4f} {currency_target}" for currency in currencies_other)
    legend: list[tuple[str, str]] = [
        *LEGEND_PARTS,
        ("Cost", f"In {currency_target}, VAT included" + (f", converted at {rates_shown}" if rates_shown else "")
         + "; ≈ marks an estimate or a reference price."),
    ]

    def row_total_build(label: str, origins: tuple[str, ...], exact: bool = False, bold: bool = False) -> str:
        cells = [
            money_format(*sums_currency[currency].sum_get(*origins)) if exact
            else money_approx_format(*sums_currency[currency].sum_get(*origins))
            for currency in currencies
        ]
        if bold:
            label, cells = f"**{label}**", [f"**{cell}**" for cell in cells]
        return f"| {label} | " + " | ".join(cells) + " |"

    has_shipping = bool(rows_shipping)
    has_optional = any(flag_yes_check(row["optional"]) for row in rows_counted)
    lines: list[str] = [
        "# Bill of Materials",
        f"Generated by `bom/bom.py` from `bom/bom.csv` on {date.today().isoformat()} - do not edit by hand.",
        "",
        "Every part of the device, its cost and its dimensions. The terms in the table headers link to the [Legend](#legend) at the end.",
        "",
        "## Parts",
        *table_parts_build(rows_parts, rows_shipping, currency_target, rates),
        "",
    ]
    if rows_small:
        lines += [
            "## Small Parts",
            "Needed, but at hand or negligible in cost - not counted in the totals.",
            "",
            *table_small_build(rows_small),
            "",
        ]
    lines += [
        "## Total",
        f"| | [Cost ({currency_target})](#legend) | " + " | ".join(f"Cost ({currency})" for currency in currencies_other) + (" |" if currencies_other else ""),
        "|---|" + "---|" * len(currencies),
        row_total_build("Ordered" + (" (shipping included)" if has_shipping else ""), ("ordered",), exact=True),
        row_total_build("Planned" + (" (optional parts not counted)" if has_optional else ""), ("planned", "printed")),
        row_total_build("Estimated spend", ("ordered", "planned", "printed"), bold=True),
    ]
    if sums_currency[currency_target].sum_get("at hand")[1]:
        lines += [
            row_total_build("At hand (reference)", ("at hand",)),
            row_total_build("Full build value", ("ordered", "planned", "printed", "at hand"), bold=True),
        ]
    lines.append("")
    if dimensions:
        lines += [
            "## Dimensions",
            "In mm, as length × width × height, from `bom/dimensions.csv`. These mirror the values in the CAD's parts (see `cad/README.md`); change both together.",
            "",
            *table_dimensions_build(dimensions, names),
            "",
        ]
        legend.append(LEGEND_SOURCE)
        lines_validation = table_validation_build(dimensions, names)
        if len(lines_validation) > 2:
            dates = sorted({dimension["checked"] for dimension in dimensions if dimension["checked"] and dimension["verdict"]})
            lines += [
                "### Dimensions Validation",
                "Which value the CAD uses, and why, where the makers' values and the measurements differ or one of them is missing."
                + (f" Checked on {', '.join(dates)} against the datasheets and listings linked above." if dates else ""),
                "",
                *lines_validation,
                "",
            ]
            legend.append(LEGEND_VERDICT)
    lines += ["## Legend", "| Term | Meaning |", "|---|---|", *(f"| **{term}** | {meaning} |" for term, meaning in legend), ""]
    MD_BOM.write_text("\n".join(lines), encoding="utf-8")

    sums = sums_currency[currency_target]
    print(f"Ordered:         {money_format(*sums.sum_get('ordered'))} {currency_target}")
    print(f"Planned:         {money_format(*sums.sum_get('planned', 'printed'))} {currency_target}")
    print(f"Estimated spend: {money_format(*sums.sum_get('ordered', 'planned', 'printed'))} {currency_target}")
    if sums.sum_get("at hand")[1]:
        print(f"At hand:         ≈ {money_format(*sums.sum_get('at hand'))} {currency_target} (reference)")
    count_to_measure = sum(dimension["used"] == "estimate" or dimension["verdict"] == "to measure" for dimension in dimensions)
    if count_to_measure:
        print(f"Dimensions:      {count_to_measure} still to measure")
    print(f"Written: {MD_BOM.relative_to(DIRECTORY_BOM.parent)}")


if __name__ == "__main__":
    bom_generate()
