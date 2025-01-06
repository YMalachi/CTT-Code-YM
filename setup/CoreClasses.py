# Here I define core classes of the project, this serves as a base to most of the logic and tools.

import os


class DataContainer:
    def __init__(self, data_path):
        """
        This class is the base for all data manipulations, it solely contains the folder with all test subjects data.
        :param data_path:
        """
        if not isinstance(data_path, str):
            raise TypeError("data_path must be a string.")
        self.data_path = data_path

    def __repr__(self):
        return f"DataContainer(data_path={self.data_path})"

class ProcessingContainer(DataContainer):
    def __init__(self, data_path, subject_name, pl_path = None, uni_path = None, default_flag = True):
        """
        This is the base class for all processing procedures. It contains all necessary information for processing
        purposes. Each test subject should have one of these, otherwise processing won't work with this subject.

        :param data_path: Path to the entire data of all the test subjects folder. This will be passed to create a DataContainer instance.
        :param subject_name: The name of the subject as written in the folder (e.g. YM696).
        :param default_flag: A bool with value True if you're using the default data structure as mentioned in the documentation
        """
        super().__init__(data_path=data_path)
        self.data_path = data_path
        self.subject_name = subject_name
        self.default_flag = default_flag
        rec_path_intermediate = os.path.join(self.data_path, subject_name)
        self.rec_path = os.path.join(rec_path_intermediate, 'REC_ET')  # this is the first directory in each subject
        if not os.path.isdir(self.rec_path): # check if it exists
            raise FileNotFoundError(f"The required directory does not exist: {self.rec_path}")

        if self.default_flag is True:
            # Construct and check paths
            try:
                # PL paths
                self.pl_path = os.path.join(self.rec_path, 'PL')
                os.path.isdir(self.pl_path)
                if not os.path.isdir(self.pl_path):
                    raise FileNotFoundError(f"The required directory does not exist: {self.pl_path}")

                # Unity paths
                self.uni_path = os.path.join(self.rec_path, 'UNI')
                if not os.path.isdir(self.uni_path):
                    raise FileNotFoundError(f"The required directory does not exist: {self.uni_path}")

            except FileNotFoundError as e:
                raise e

            except Exception as e:
                # catch any other unexpected errors
                raise RuntimeError(f"An unexpected error occurred: {e}")

        # If default_flag is False then we require pl_path and uni_path as input
        elif pl_path or uni_path is None:
            raise TypeError(f"If your data doesn't have a default structure, please provide pl_path and uni_path as well")

        else:
            self.pl_path = pl_path
            self.uni_path = uni_path





