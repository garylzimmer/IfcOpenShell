# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import re
import pathlib
import ifcopenshell
import ifcopenshell.util.schema
from ifcopenshell.entity_instance import entity_instance
from functools import lru_cache
from typing import List, Generator, Optional

templates = {}


def get_template(schema):
    global templates
    if schema not in templates:
        templates[schema] = PsetQto(schema)
    return templates[schema]


class PsetQto:
    templates_path = {
        "IFC4": "Pset_IFC4_ADD2.ifc",
    }

    def __init__(self, schema: str, templates=None) -> None:
        self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema)
        if not templates:
            folder_path = pathlib.Path(__file__).parent.absolute()
            path = str(folder_path.joinpath("schema", self.templates_path[schema]))
            templates = [ifcopenshell.open(path)]
        self.templates = templates

    @lru_cache()
    def get_applicable(
        self, ifc_class="", predefined_type="", pset_only=False, qto_only=False
    ) -> List[entity_instance]:
        any_class = not ifc_class
        if not any_class:
            entity = self.schema.declaration_by_name(ifc_class)
        result = []
        for template in self.templates:
            for prop_set in template.by_type("IfcPropertySetTemplate"):
                if pset_only:
                    if prop_set.Name.startswith("Qto_"):
                        continue
                if qto_only:
                    if not prop_set.Name.startswith("Qto_"):
                        continue
                if any_class or self.is_applicable(entity, prop_set.ApplicableEntity or "IfcRoot", predefined_type):
                    result.append(prop_set)
        return result

    @lru_cache()
    def get_applicable_names(self, ifc_class: str, predefined_type="", pset_only=False, qto_only=False) -> List[str]:
        """Return names instead of objects for other use eg. enum"""
        return [prop_set.Name for prop_set in self.get_applicable(ifc_class, predefined_type, pset_only, qto_only)]

    def is_applicable(self, entity: entity_instance, applicables: str, predefined_type="") -> bool:
        """applicables can have multiple possible patterns :
        IfcBoilerType                               (IfcClass)
        IfcBoilerType/STEAM                         (IfcClass/PREDEFINEDTYPE)
        IfcBoilerType[PerformanceHistory]           (IfcClass[PerformanceHistory])
        IfcBoilerType/STEAM[PerformanceHistory]     (IfcClass/PREDEFINEDTYPE[PerformanceHistory])
        """
        for applicable in applicables.split(","):
            match = re.match(r"(\w+)(\[\w+\])*/*(\w+)*(\[\w+\])*", applicable)
            if not match:
                continue
            # Uncomment if usage found
            # applicable_perf_history = match.group(2) or match.group(4)
            if predefined_type and predefined_type != match.group(3):
                continue

            applicable_class = match.group(1)
            if ifcopenshell.util.schema.is_a(entity, applicable_class):
                return True
        return False

    @lru_cache()
    def get_by_name(self, name: str) -> Optional[entity_instance]:
        for template in self.templates:
            for prop_set in template.by_type("IfcPropertySetTemplate"):
                if prop_set.Name == name:
                    return prop_set
        return None

    def is_templated(self, name: str) -> bool:
        return bool(self.get_by_name(name))
