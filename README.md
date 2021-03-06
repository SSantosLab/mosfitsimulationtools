 ## MOSFiT Simulation Tools
 Kamile Lukosiute, January 2019
 
 
 [MOSFiT](https://github.com/SSantosLab/MOSFiT) Simulation Tools (MST) are tools for simulating observations with MOSFiT, specifically the Kasen model included in the SSantosLab version of MOSFiT, and analyzing the output. There are two main scripts included: simulate.py and analyze.py. Simulate contains objects needed for simulation, while analyze contains objects needed for analysis. Additionally, there is a plotting module. 
 
 How simulate and analyze should be used is shown in test_creation_mst.py and test_analysis_mst.py, respectively. The figures that should be produced by test_analysis.py are provided in tests/test/.
 
 /test/ is the directory structure that is created by running test_creation_mst.py (and following the shell instructions) and  test_analysis_mst.py. This directory can be deleted in its entirety if it is taking up space on your computer.
 
For actual usage by people who aren't me, I suggest that you don't bother trying to make it into an installable package and instead do:
```python
import sys
sys.path.append('direcotry/containing/mosfitsimulationtools/')
import mosfitsimulationtools as mst

data = mst.simulate.Single(...options...)
```
