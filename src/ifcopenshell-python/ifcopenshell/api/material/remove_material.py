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

import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"material": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        inverse_elements = self.file.get_inverse(self.settings["material"])
        self.file.remove(self.settings["material"])
        # TODO: this is probably not robust enough
        # TODO: purge material definition representation
        for inverse in inverse_elements:
            if inverse.is_a("IfcMaterialConstituent"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcMaterialLayer"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcMaterialProfile"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssociatesMaterial"):
                self.file.remove(inverse)
