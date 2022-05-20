#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
import argparse
import pathlib
from typing import List, Optional
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Flight:
    stay: str
    number: str
    value: str


@dataclass
class Listing:
    flights: List[Flight] = field(default_factory=lambda: [])

    def adding(self, stay:str, number:str, value:str) -> None:
        self.flights.append(
            Flight(
                stay=stay,
                number=number,
                value=value
            )
        )

    def table(self) -> str:
        """Вывод скиска рейсов"""
        table = []
        line: str = '+-{}-+-{}-+-{}-+-{}-+'.format(
                    '-' * 4,
                    '-' * 20,
                    '-' * 15,
                    '-' * 16
                )
        table.append(line)
        table.append(
            '| {:^4} | {:^20} | {:^15} | {:^16} |'.format(
                "№",
                "Место прибытия",
                "Номер самолёта",
                "Тип"
            )
        )
        table.append(line)
        for i, num in enumerate(self.flights, 1):
            table.append(
                '| {:<4} | {:<20} | {:<15} | {:<16} |'.format(
                    i,
                    num.get('stay', ''),
                    num.get('number', ''),
                    num.get('value', 0)
                )
            )
        table.append(line)
        return '\n'.join(table)

    def selecting(self, nom:str) -> List[str]:
        """Выбор рейсов по типу самолёта"""
        count = 0
        result = []
        for i, num in enumerate(self.flights, 1):
            if nom == num.get('value', ''):
                count += 1
                result.append(
                    '| {:<4} | {:<20} | {:<15} | {:<16} |'.format(
                        count,
                        num.get('stay', ''),
                        num.get('number', ''),
                        num.get('value', 0)
                    )
                )

        return result
        
    def load(self, filename:str) -> str:
        with open(filename, 'r', encoding='utf8') as fin:
            xml = fin.read()
        parser = ET.XMLParser(encoding="utf8")
        tree = ET.fromstring(xml, parser=parser)
        self.flights = []
        for flight_element in tree:
            stay, number, value = None, None, None
            for element in flight_element:
                if element.tag == 'stay':
                    stay = element.text
                elif element.tag == 'number':
                    number = element.text
                elif element.tag == 'value':
                    value = element.text
                if stay is not None and number is not None and value is not None:
                    self.flights.append(
                        Flight(
                            stay=stay,
                            number=number,
                            value=value
                        )
                    )
        return filename

    def save(self, filename:str) -> None:
        root = ET.Element('flights')
        for flight in self.flights:
            flights_element = ET.Element('flights')
            stay_element = ET.SubElement(flights_element, 'stay')
            stay_element.text = flight.stay

            number_element = ET.SubElement(flights_element, 'number')
            number_element.text = flight.number
            value_element = ET.SubElement(flights_element, 'value')
            value_element.text = flight.value
            root.append(flights_element)
        tree = ET.ElementTree(root)
        with open(filename, 'wb') as fout:
            tree.write(fout, encoding='utf8', xml_declaration=True)


def main(command_line:Optional[str]=None) -> None:
    staff = Listing()
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "filename",
        action="store",)
    parser = argparse.ArgumentParser("flights")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command")
    add = subparsers.add_parser(
        "add",
        parents=[file_parser])
    add.add_argument(
        "-s",
        "--stay",
        action="store",
        required=True,)
    add.add_argument(
        "-v",
        "--value",
        action="store",
        required=True,)
    add.add_argument(
        "-n",
        "--number",
        action="store",
        required=True,)
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],)
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],)
    select.add_argument(
        "-t",
        "--type",
        action="store",
        required=True,)
    args = parser.parse_args(command_line)
    is_dirty = False
    name = args.filename
    names = pathlib.Path.cwd()/name

    if names.exists():
        filename = staff.load(name)
    else:
        filename = args.filename

    if args.command == "add":
        staff.adding(args.stay, args.number, args.value)
        is_dirty = True
    elif args.command == 'display':
        staff.table()
    elif args.command == "select":
        staff.selecting(args.type)
    if is_dirty:
        staff.save(filename)


if __name__ == '__main__':
    main()
