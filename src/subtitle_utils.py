# TODO make submodule and combine with my_movie_tools and Youtube_utils, thats probably it but check for more
from pathlib import Path
import pysubs2
from sms.file_system_utils import file_system_utils as fsu

def shift_and_trim_subs(in_sub_file_path, out_sub_file_path, shift_num_ms):
    fsu.delete_if_exists(out_sub_file_path)
    Path(out_sub_file_path).parent.mkdir(parents=True, exist_ok=True)

    in_subs = pysubs2.load(in_sub_file_path, encoding="utf-8")

    in_subs.shift(ms = shift_num_ms)

    print(f"Saving shifted/trimmed subs to {out_sub_file_path=}...")
    in_subs.save(out_sub_file_path)

