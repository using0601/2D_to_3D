#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#

import os
import logging
from argparse import ArgumentParser
import shutil

# This Python script is based on the shell converter script provided in the MipNerF 360 repository.
parser = ArgumentParser("Colmap converter")
parser.add_argument("--no_gpu", action='store_true')
parser.add_argument("--source_path", "-s", required=True, type=str)
parser.add_argument("--camera", default="OPENCV", type=str)
parser.add_argument("--colmap_executable", default="", type=str)
args = parser.parse_args()
colmap_command = '"{}"'.format(args.colmap_executable) if len(args.colmap_executable) > 0 else "colmap"
use_gpu = 1 if not args.no_gpu else 0

os.makedirs(os.path.join(args.source_path, "sparse"), exist_ok=True)

## Feature extraction
feat_extracton_cmd = (colmap_command + " feature_extractor"
    + " --database_path " + os.path.join(args.source_path, "database.db")
    + " --image_path " + os.path.join(args.source_path, "input")
    + " --ImageReader.single_camera 1"
    + " --ImageReader.camera_model " + args.camera
    + " --SiftExtraction.use_gpu " + str(use_gpu))
exit_code = os.system(feat_extracton_cmd)
if exit_code != 0:
    logging.error(f"Feature extraction failed with code {exit_code}. Exiting.")
    exit(exit_code)

## Feature matching
feat_matching_cmd = (colmap_command + " exhaustive_matcher"
    + " --database_path " + os.path.join(args.source_path, "database.db")
    + " --SiftMatching.use_gpu " + str(use_gpu))
exit_code = os.system(feat_matching_cmd)
if exit_code != 0:
    logging.error(f"Feature matching failed with code {exit_code}. Exiting.")
    exit(exit_code)

### Bundle adjustment
# The default Mapper tolerance is unnecessarily large,
# decreasing it speeds up bundle adjustment steps.
mapper_cmd = (colmap_command + " mapper"
    + " --database_path " + os.path.join(args.source_path, "database.db")
    + " --image_path "  + os.path.join(args.source_path, "input")
    + " --output_path "  + os.path.join(args.source_path, "sparse")
    + " --Mapper.ba_global_function_tolerance=0.000001")
exit_code = os.system(mapper_cmd)
if exit_code != 0:
    logging.error(f"Mapper failed with code {exit_code}. Exiting.")
    exit(exit_code)

print("Done.")
