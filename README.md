# bbox_query
Utility for retrieving points within  a polygon from an EPT. Currently writes them to a `.las` file.

__Future:__ Includes options to write common raster derivatives and/or return the pointcloud.  Also can accept a custom PDAL pipeline.

# Usage
## Set up environment
This depends on pdal and geopandas. If you do not have an environment set up with the dependenies, first prepare your environment (or alternately you can run program from a docker,explained below)). The `environment.yaml` file which is included can be used to create and envirnment with conda. In a directory with the yaml, in the terminal type:

```conda env create -f environment.yml```

This will create an environment call `pdal+`.

`app_ept.py [-h] [--vector VECTORFILE] [--vector_dir DIRECTORY] --ept EPT  --out OUT`
 
 optional arguments:
  `-h, --help`               Show this help message and exit
  `--vector VECTOR`          Path to vector file for which points will be returned.
  `--vector_dir VECTOR_DIR`  Path to vector files for which points will be returned as seperate laz files.
  `--ept EPT`                Path to ept
  `--out OUT`                Path to output directory

__Example:__
```./app_ept.py --ept=https://some_stinkin_bucket/entwine/ept.json --out=data --vector=asgard.shp```

## Run from container.
Coming soon. 

### This uses PDAL, the license for which is as follows:

Copyright (c) 2019, Hobu, Inc. (howard@hobu.co)

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

    Neither the name of Hobu, Inc. or Flaxen Consulting LLC nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
