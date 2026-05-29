# PyInstaller runtime hook - must patch BEFORE numpy imports
import sys
import importlib.abc
import importlib.machinery

# Patch at the module loader level to intercept numpy imports
class NumpyPatcher(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_module(self, fullname, path=None):
        if fullname.startswith('numpy'):
            return self
        return None
    
    def load_module(self, fullname):
        # Let normal import happen, but catch the error
        try:
            # Use the parent import mechanism
            import importlib.util
            spec = importlib.util.find_spec(fullname)
            if spec and spec.loader:
                # Try to load normally first
                return spec.loader.load_module(fullname)
        except TypeError as e:
            if 'docstring' in str(e):
                # Monkey-patch numpy.core.overrides before retry
                if 'numpy.core.overrides' in fullname or fullname == 'numpy':
                    # Patch the add_docstring function globally
                    import numpy.core.overrides as ov
                    if hasattr(ov, 'add_docstring'):
                        orig = ov.add_docstring
                        def fixed_add_docstring(func, docstring):
                            if docstring is None or not isinstance(docstring, str):
                                docstring = ""
                            return orig(func, docstring)
                        ov.add_docstring = fixed_add_docstring
        return None

sys.meta_path.insert(0, NumpyPatcher())


