"""XML service for converting dictionaries to XML."""
from typing import Any, Dict, Union
import xml.etree.ElementTree as ET


def dict_to_xml(data: Dict[str, Any]) -> str:
    """
    Convert a dictionary to an XML string.
    
    Args:
        data: Dictionary to convert to XML
        
    Returns:
        XML string representation of the dictionary
    """
    if not data:
        return ""
    
    # Get the root key and value
    root_key = list(data.keys())[0]
    root_value = data[root_key]
    
    root = ET.Element(root_key)
    _dict_to_xml_recursive(root, root_value)
    
    return ET.tostring(root, encoding='unicode')


def _dict_to_xml_recursive(parent: ET.Element, data: Any) -> None:
    """
    Recursively convert dictionary data to XML elements.
    
    Args:
        parent: Parent XML element
        data: Data to convert (dict, list, or value)
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key.startswith('@'):
                # Handle attributes
                attr_name = key[1:]
                parent.set(attr_name, str(value))
            elif key == '#text':
                # Handle text content
                parent.text = str(value)
            else:
                # Handle nested elements
                if isinstance(value, list):
                    for item in value:
                        child = ET.SubElement(parent, key)
                        if isinstance(item, dict):
                            _dict_to_xml_recursive(child, item)
                        else:
                            child.text = str(item)
                elif isinstance(value, dict):
                    child = ET.SubElement(parent, key)
                    _dict_to_xml_recursive(child, value)
                else:
                    child = ET.SubElement(parent, key)
                    child.text = str(value)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                _dict_to_xml_recursive(parent, item)
            else:
                parent.text = str(item)
    else:
        parent.text = str(data)
