"""
Extract by location
"""

import json
import logging
import os
from pathlib import Path
import sys

from merge_rasters import merge_rasters

LOG_FORMAT = '[%(levelname)s] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=LOG_FORMAT)


def load_inputs(input_path):
    inputs_desc = json.load(open(input_path))
    inputs = inputs_desc.get('inputs')
    parameters = inputs_desc.get('parameters')
    return inputs, parameters


def main():
    WORKING_DIR = os.getenv('DELAIRSTACK_PROCESS_WORKDIR')
    if not WORKING_DIR:
        raise KeyError('DELAIRSTACK_PROCESS_WORKDIR environment variable must be defined')
    WORKING_DIR = Path(WORKING_DIR).resolve()

    logging.debug('Extracting inputs and parameters...')

    # Retrieve inputs and parameters from inputs.json
    inputs, parameters = load_inputs(WORKING_DIR / 'inputs.json')

    # Get info for the inputs
    rasters_in = inputs['rasters_in']
    if not isinstance(rasters_in, list):
        rasters_in = [rasters_in]
    rasters_path = []
    for component in rasters_in:
        rasters_path.append(component['components'][0]['path'])
        logging.info(f'Component path: {component["components"][0]["path"]}')

    logging.info(f'Rasters datasets path: {rasters_path}')

    out_filename = parameters.get('outraster_name')
    if out_filename is not None:
        out_filename_ok = out_filename
    else:
        out_filename_ok = 'Merged_rasters'
    logging.info(f'Outfile name: {out_filename_ok} ')

    # Create the output vector
    logging.debug('Creating the output raster')
    out_filename_ext = out_filename_ok + '.tif'
    outpath = WORKING_DIR / out_filename_ext
    logging.info(f'Output path: {outpath}')

    # Create geosjon
    logging.info('Merge rasters')
    merge_rasters(
        raster_files=rasters_path,
        outfile_path=outpath)

    # Create the outputs.json to describe the deliverable and its path
    logging.debug('Creating the outputs.json')
    output = {
        "outputs": {
            "merged_rasters": {  # Must match the name of deliverable in extract_mp.yaml
                "type": "raster",
                "format": "tif",
                "name": out_filename_ok,
                "categories": component['categories'],
                "components": [
                    {
                        "name": "raster",
                        "path": str(outpath)
                    }
                ]
            },
        },
        "version": "0.1"
    }
    with open(WORKING_DIR / 'outputs.json', 'w+') as f:
        json.dump(output, f)

    logging.info('End of processing.')


if __name__ == '__main__':
    main()
