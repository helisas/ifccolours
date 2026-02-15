import ifcopenshell
import ifcopenshell.util.selector
from collections import defaultdict
import random
import os

def main():

    while True:

        try:
            input_file = input("Please enter IFC file path or type exit to quit: ")
            if input_file == "exit":
                return
            model = ifcopenshell.open(input_file)
            break
        except:
            print("Not a valid IFC file path.")
            pass

    while True:

        try:
            property_or_type = input("Colour by property or type? Type p for property, t for type or type exit to quit: ")
            if property_or_type == "exit":
                return
            if not (property_or_type == "p" or property_or_type == "t"):
                raise Exception
            break
        except:
            print("Please type p, t, or exit")
            pass

    print(property_or_type)

    while True:

        try:
            pset = input("Please enter Pset name (example: Pset_WallCommon) or type exit to quit: ")
            if pset == "exit":
                return
            if check_pset_exists(model, pset) == False:
                raise Exception
            break
        except:
            print("Pset not found.")
            pass
    
    while True:

        try:
            property = input("Please enter property name (example: FireRating) or type exit to quit: ")
            if property == "exit":
                return
            elements = ifcopenshell.util.selector.filter_elements(model, f"IfcElement, {pset}.{property} != NULL")
            if not elements:
                raise Exception
            break
        except:
            print("No elements with the requested property found in the Pset.")
            pass

    
    elements_with_properties = [Element(element, ifcopenshell.util.element.get_pset(element, pset, property)) for element in elements]
    
    grouped = defaultdict(list)

    for e in elements_with_properties:
        grouped[e.property].append(e)

    for property, group in grouped.items():
        
        r = random.random()
        g = random.random()
        b = random.random()
        
        style = ifcopenshell.api.style.add_style(model)

        ifcopenshell.api.style.add_surface_style(model,
            style=style, ifc_class="IfcSurfaceStyleShading", attributes={
                "SurfaceColour": { "Name": None, "Red": r, "Green": g, "Blue": b },
                "Transparency": 0.0,
            })
        for e in group:

            representation = ifcopenshell.util.representation.get_representation(e.element, context="Model", subcontext="Body")
            ifcopenshell.api.style.assign_item_style(model, style=style, item=representation.Items[0])
            
    new_file_name = get_available_filename(input_file)
    model.write(new_file_name)       


def check_pset_exists(ifc_file, pset_name):
    
    property_sets = ifc_file.by_type("IfcPropertySet")

    for pset in property_sets:
        if pset.Name == pset_name:
            return True

    return False

def get_available_filename(file_path):
    
    original_file_name_split = file_path.split(r".")
    
    counter = 1
    while os.path.exists(file_path):
        
        file_path = (original_file_name_split[0] + "_coloured" + str(counter) + "." + original_file_name_split[1])

        counter += 1
        
    return file_path

class Element:
    def __init__(self, element, property):
        self.element = element
        self.property = property

if __name__ == "__main__":
    main()




