# MoST: MOdular Scheduling Transforms

A representation for higher-level transforms, with tools to generate [EXO](https://github.com/ChezJrk/exo) code.

## Setup

This has been extensively tested on Python 3.9.7. Python versions 3.7 and earlier are not supported as Exo requires several newer language features not available.

```
git clone https://github.com/gdinh/MoST.git
cd MoST
python -m venv $HOME/.venv/most
source $HOME/.venv/most/bin/activate
python -m pip install pip setuptools wheel
python -m pip install -r requirements.txt
```

If you'd like to run the interactive demos/documentation, install iPython and set it up so that it points to your venv by running these *from within the venv*:

```
python -m pip install jupyter
ipython kernel install --user --name=MoST_venv
```

Now, you'll be able to launch `jupyter notebook`; just navigate to `docs/` and open `most_demo.ipynb`, then point the notebook to the venv using Kernel > Change kernel > MoST_venv.

## Project status:
- Tiling schedule works
- HBL projective optimal tiling works for constant loop bounds

In progress:
- [GPTune](https://gptune.lbl.gov/) integration

Next TODOs:
- [CoSA](https://github.com/ucb-bar/cosa) transform
- HBL autotiling for CNNs
- Code specialization for variable sized bounds (blocked on SysTL specialization support)
