
import argparse
import numpy as np
import numpy.typing as npt
from typing import List

from ase.atoms import Atoms
from ase.io.trajectory import Trajectory

def filter_local_minima(atoms: List[Atoms], significant_figures: int) -> npt.NDArray:
    """
    Remove similar local minima from the list based on the relevant number significant figures of the potential energy.

    Parameters
    ----------
    atoms: List[Atoms]
        All local minima found
    significant_figures: int
        Number of significant figures to round the potential energy to to find the unique local minima
    
    Returns
    -------
    atoms: ndarray
        List of all unique local minima
    """
    # Initialise atoms array first because ase.atoms.Atoms will be unpacked by numpy into an array of ase.atom.Atom
    _atoms = np.empty(len(atoms), dtype=object)
    # Sort atoms by ascending potential energy
    _atoms[:] = sorted(atoms, key=lambda a: a.get_potential_energy())
    # Get all potential energies
    potential_energies = np.array([a.get_potential_energy() for a in _atoms])
    # Remove values above zero
    indexes = potential_energies < 0
    _atoms = _atoms[indexes]
    potential_energies = potential_energies[indexes]

    # Rounding
    # 1. Calculate order of magnitude in 10^i
    order_of_magnitudes = np.floor(np.log10(np.abs(potential_energies))).astype(np.int32)
    # 2. Calculate position of msd in relation to the decimal point
    positions_msd = -(order_of_magnitudes + 1)
    # 3. Calculate position for rounding to significant figures in relation to the decimal point
    rounding = positions_msd + significant_figures
    # 4. Round energies
    rounded = np.array([round(energy, d) for (energy, d) in zip(potential_energies, rounding)])

    # Only keep unique
    _, indexes = np.unique(rounded, return_index=True)
    _atoms = _atoms[indexes]
    potential_energies = potential_energies[indexes]
    
    return _atoms

def filter_trajectory(input: str, significant_figures: int, output: str=None):
    """
    Remove similar local minima from a trajectory based on the relevant number significant figures of the potential energy.

    Parameters
    ----------
    input: str
        File path to the input trajectory
    significant_figures: int
        Number of significant figures to round the potential energy to to find the unique local minima
    output: str, None (optional)
        File path to the trajectory to store filtered local minima
        If None, the input file will be replaced by the new trajectory with filtered local minima
    """
    if output is None:
        output = input
    # Load input trajectory
    trajectory = Trajectory(input)
    # Filter atoms
    atoms = filter_local_minima(trajectory[:], significant_figures)
    # Close trajectory
    trajectory.close()

    # Load output trajectory
    trajectory = Trajectory(output, 'w')
    # Write atoms
    for a in atoms:
        trajectory.write(a)
    # Close trajectory
    trajectory.close()

def main(**kwargs):
    filter_trajectory(kwargs.get('input'), kwargs.get('output', None), kwargs.get('significant_figures', 2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="Input file")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output file (default = input file)")
    parser.add_argument("-s", "--significant-figures", type=int, default=2, help="Significant figures to round the potential energy to to check for uniqueness")

    args = parser.parse_args()

    main(**vars(args))