# MoST: MOdular Scheduling Transforms

A representation for higher-level transforms, with tools to generate [SysTL](https://github.com/ChezJrk/SYS_ATL) code.

Source organization:

```
├── most_base.py: main interface, common libraries, etc.
├── docs - not just documentation, but papers, working drafts, etc.
├── qast_utils - Utilities for generating semantic data from QAST object; necessary to 
└── transforrms - specific instances of transforms. Automatic bits are currently factory methods in these objects.
    └── TilingSchedule.py
```

Design goals can be found under docs/design-goals-and-overview.lyx.

To install, put it in the root directory of a SysTL install, and add the parent of the MoST directory (normally just the SysTL directory) to your venv path. That is:

- Find the site_packages directory with `python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")`
- Create a new file (name isn't important; I use `sysatl_venv_root.pth`) with the above directory (e.g. `/home/eecs/dinh/SYS_ATL`) as its contents

Project status:
- Tiling schedule works
- HBL projective optimal tiling works for constant loop bounds

In progress:
- [GPTune](https://gptune.lbl.gov/) integration

Next TODOs:
- [CoSA](https://github.com/ucb-bar/cosa) transform
- HBL autotiling for CNNs
- Code specialization for variable sized bounds (blocked on SysTL specialization support)
