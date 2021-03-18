# geodemo

[![image](https://img.shields.io/pypi/v/geodemo.svg)](https://pypi.python.org/pypi/geodemo)
[![image](https://img.shields.io/conda/vn/conda-forge/geodemo.svg)](https://anaconda.org/conda-forge/geodemo)
[![image](https://pepy.tech/badge/geodemo)](https://pepy.tech/project/geodemo)
[![image](https://github.com/giswqs/geodemo/workflows/docs/badge.svg)](https://geodemo.gishub.org)
[![image](https://github.com/giswqs/geodemo/workflows/build/badge.svg)](https://github.com/giswqs/geodemo/actions?query=workflow%3Abuild)
[![image](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A Python package for interactive mapping**


-   Free software: MIT license
-   Documentation: https://giswqs.github.io/geodemo
    
## Installation

### pip

```
pip install geodem
```

## How to publish a Python package on conda-forge

1. Install conda-build using: `conda install conda-build`
2. Create the conda recipe using: `conda skeleton pypi package-name`
3. Make changes to the recipe (**meta.yaml**) by following this [example](https://github.com/giswqs/geodemo/blob/master/recipe/meta.yaml). A few key items to change: add `noarch: python` under the `build` section; remove all packages except `pip` and `python` from the `host` section; specify a python version (e.g., >=3.6) for both the `host` and `run` sections; add `LICENSE`, `doc_url`, and `dev_url` to the `about` section; add your GitHub username to the `recipe-maintainers` section.
4. Fork <https://github.com/conda-forge/staged-recipes>
5. Add your package recipe to `staged-recipes/recipes/package-name/meta.yaml`
6. Commit changes and push to GitHub
7. Submit a pull request
8. Wait for the recipe to pass all checks
9. `@conda-forge/help-python` to let them know that your recipe is ready for review.
10. Once your recipe is accepted, your package should appear on conda-forge within a few hours.
11. The link to your package on conda-forage should be https://anaconda.org/conda-forge/package-name, such as <https://anaconda.org/conda-forge/geemap>


## Credits

This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [giswqs/pypackage](https://github.com/giswqs/pypackage) project template.
