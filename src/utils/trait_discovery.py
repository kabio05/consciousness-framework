import os
import importlib.util  # Need to import importlib.util specifically
import importlib.machinery
import inspect
from pathlib import Path
from typing import Dict, Type, List, Optional, Any
import logging
from abc import ABC

logger = logging.getLogger(__name__)

class TraitDiscovery:
    """
    Automatically discovers and loads consciousness trait implementations
    
    This class scans the traits folder and dynamically loads any Python files
    that contain valid trait implementations, making the framework extensible
    without code modifications.
    """
    
    def __init__(self, traits_path: Optional[Path] = None):
        """
        Initialize the trait discovery system
        
        Args:
            traits_path: Path to the traits folder (defaults to src/traits)
        """
        if traits_path is None:
            # Try to find the traits folder relative to this file
            current_file = Path(__file__)
            self.traits_path = current_file.parent.parent / "traits"
        else:
            self.traits_path = Path(traits_path)
            
        self.discovered_traits: Dict[str, Type] = {}
        self.trait_metadata: Dict[str, Dict[str, Any]] = {}
        
    def discover_all_traits(self) -> Dict[str, Type]:
        """
        Discover all trait implementations in the traits folder
        
        Returns:
            Dictionary mapping trait names to their classes
        """
        if not self.traits_path.exists():
            logger.error(f"Traits path does not exist: {self.traits_path}")
            return {}
            
        # Clear previous discoveries
        self.discovered_traits.clear()
        self.trait_metadata.clear()
        
        # Scan all Python files in traits folder
        for file_path in self.traits_path.glob("*.py"):
            if file_path.name.startswith("_") or file_path.name == "base_trait.py":
                continue  # Skip private files and base class
                
            trait_name = file_path.stem  # filename without .py
            
            try:
                # Dynamically import the module
                module = self._import_trait_module(file_path, trait_name)
                
                if module:
                    # Find trait classes in the module
                    trait_classes = self._find_trait_classes(module, trait_name)
                    
                    for class_name, trait_class in trait_classes.items():
                        # Use the module name as the trait identifier
                        self.discovered_traits[trait_name] = trait_class
                        
                        # Extract metadata from the class
                        self.trait_metadata[trait_name] = self._extract_trait_metadata(trait_class)
                        
                        logger.info(f"Discovered trait: {trait_name} ({class_name})")
                        
            except Exception as e:
                logger.error(f"Error loading trait from {file_path}: {e}")
                
        return self.discovered_traits
    
    def _import_trait_module(self, file_path: Path, module_name: str):
        """Import a trait module dynamically"""
        try:
            # Create module spec
            spec = importlib.util.spec_from_file_location(
                f"traits.{module_name}", 
                file_path
            )
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            else:
                logger.error(f"Could not create spec for {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to import {module_name}: {e}")
            return None
    
    def _find_trait_classes(self, module, trait_name: str) -> Dict[str, Type]:
        """Find all valid trait classes in a module"""
        trait_classes = {}
        
        # Import BaseTrait to check inheritance
        try:
            from traits.base_trait import BaseTrait
        except ImportError:
            try:
                from src.traits.base_trait import BaseTrait
            except ImportError:
                logger.error("Could not import BaseTrait")
                return trait_classes
        
        # Look for classes that inherit from BaseTrait
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Check if it's a trait class (inherits from BaseTrait but isn't BaseTrait itself)
            if (issubclass(obj, BaseTrait) and 
                obj is not BaseTrait and 
                not name.startswith('_')):
                
                # Prefer classes with "Tester" in the name, otherwise take the first valid one
                if "Tester" in name or not trait_classes:
                    trait_classes[name] = obj
                    
        return trait_classes
    
    def _extract_trait_metadata(self, trait_class: Type) -> Dict[str, Any]:
        """Extract metadata from a trait class"""
        metadata = {
            "class_name": trait_class.__name__,
            "module": trait_class.__module__,
            "description": inspect.getdoc(trait_class) or "No description available",
            "methods": [],
            "test_types": []
        }
        
        # Extract public methods
        for method_name, method in inspect.getmembers(trait_class, inspect.ismethod):
            if not method_name.startswith('_'):
                metadata["methods"].append(method_name)
        
        # Try to extract test types if available
        if hasattr(trait_class, 'test_battery'):
            try:
                # This would need an instance, so we'll skip for now
                metadata["test_types"] = ["Scene Building", "Perceptual Binding", "etc."]
            except:
                pass
                
        return metadata
    
    def get_trait_info(self, trait_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a specific trait"""
        return self.trait_metadata.get(trait_name)
    
    def list_available_traits(self) -> List[str]:
        """Get a list of all available trait names"""
        return list(self.discovered_traits.keys())
    
    def instantiate_trait(self, trait_name: str, api_client: Any) -> Optional[Any]:
        """
        Create an instance of a trait tester
        
        Args:
            trait_name: Name of the trait to instantiate
            api_client: API client to pass to the trait constructor
            
        Returns:
            Instance of the trait tester or None if not found
        """
        trait_class = self.discovered_traits.get(trait_name)
        
        if not trait_class:
            logger.error(f"Trait not found: {trait_name}")
            return None
            
        try:
            # Most trait testers expect an api_client parameter
            instance = trait_class(api_client)
            return instance
        except Exception as e:
            logger.error(f"Failed to instantiate trait {trait_name}: {e}")
            return None
    
    def validate_trait_implementation(self, trait_name: str) -> Dict[str, bool]:
        """
        Validate that a trait properly implements required methods
        
        Returns dictionary of validation results
        """
        trait_class = self.discovered_traits.get(trait_name)
        
        if not trait_class:
            return {"exists": False}
            
        validation = {
            "exists": True,
            "has_generate_test_suite": hasattr(trait_class, 'generate_test_suite'),
            "has_evaluate_responses": hasattr(trait_class, 'evaluate_responses'),
            "has_run_comprehensive_assessment": hasattr(trait_class, 'run_comprehensive_assessment'),
            "is_instantiable": False
        }
        
        # Try to instantiate with a mock client
        try:
            class MockClient:
                def query(self, prompt):
                    return "Mock response"
                    
            instance = trait_class(MockClient())
            validation["is_instantiable"] = True
        except:
            pass
            
        return validation


# Singleton instance for global access
_trait_discovery = None

def get_trait_discovery() -> TraitDiscovery:
    """Get or create the global trait discovery instance"""
    global _trait_discovery
    if _trait_discovery is None:
        _trait_discovery = TraitDiscovery()
    return _trait_discovery


# Example usage and testing
if __name__ == "__main__":
    """Test the trait discovery system"""
    
    discovery = TraitDiscovery()
    
    print("🔍 Discovering consciousness traits...")
    traits = discovery.discover_all_traits()
    
    print(f"\n📦 Found {len(traits)} traits:")
    for trait_name in traits:
        info = discovery.get_trait_info(trait_name)
        print(f"\n  • {trait_name}:")
        print(f"    Class: {info['class_name']}")
        print(f"    Description: {info['description'][:100]}...")
        
        # Validate implementation
        validation = discovery.validate_trait_implementation(trait_name)
        print(f"    Valid: {all(validation.values())}")