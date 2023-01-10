import os
from pathlib import Path
from sms.file_system_utils import file_system_utils as fsu

class Clip_Dir_Data:
    mp4_path = False
    auto_sub_path = False

    def __init__(self, clip_dir_path):
        self.clip_dir_path = clip_dir_path
        self.clip_name = Path(clip_dir_path).name

        self._set_mp4_and_auto_sub_paths()

        # print("end of init")

    def has_subs(self):
        return not (self.auto_sub_path == None)

    def _set_mp4_and_auto_sub_paths(self):
        # clip_dir_path will pretty much always contain 1 .mp4 and 1 .srt, .mp4 is required, .srt optional, error if > 2 files in dir
        clip_dir_file_path_l = fsu.get_dir_content_l(self.clip_dir_path, "file")
        if len(clip_dir_file_path_l) > 2:
            raise Exception(f"ERROR: {len(clip_dir_file_path_l)} > 2, dir can contain 2 files at most (1 .srt and 1.mp4) {clip_dir_file_path_l=}")

        # No dirs allowed
        clip_dir_dir_path_l = fsu.get_dir_content_l(self.clip_dir_path, "dir")
        if len(clip_dir_dir_path_l) > 0:
            raise Exception(f"ERROR: {len(clip_dir_dir_path_l)} > 0, dir can contain no dirs")

        clip_mp4_path = os.path.join(self.clip_dir_path, self.clip_name + ".mp4")

        # .mp4 with same name required
        if not Path(clip_mp4_path).is_file():
            raise Exception(f"ERROR: {clip_mp4_path=} does not exist, {clip_dir_file_path_l=}")

        # Sub file not required, but will be .srt if exists, and is only other file allowed to exist in dir
        # However, .srt files can have different pre-suffixes like .en.srt, .en-orig.srt, .en-en.srt, etc.
        auto_sub_srt_path = None
        if len(clip_dir_file_path_l) == 2:
            sub_file_path_l = list(Path(self.clip_dir_path).glob("*.srt"))

            if len(sub_file_path_l) != 1:
                raise Exception(f"ERROR: {len(sub_file_path_l)=} != 1, if dir contains more than just 1 .mp4 file, that means it must contain 1 .srt file, 2 files in dir, but 0 .srt files found, {clip_dir_file_path_l=}")

            auto_sub_srt_path = sub_file_path_l[0]

        self.mp4_path = clip_mp4_path
        self.auto_sub_path = auto_sub_srt_path

        # print("all good",clip_dir_file_path_l)


class YT_PL_DL_Data:
    clip_dir_data_l = []
    def __init__(self, in_dir_path):
        self.dir_path = in_dir_path

        clip_dir_path_l = fsu.get_dir_content_l(in_dir_path, "dir")
        for clip_dir_path in clip_dir_path_l:
            new_clip_dir_data = Clip_Dir_Data(clip_dir_path)
            self.clip_dir_data_l.append(new_clip_dir_data)


if __name__ == "__main__":
    import os.path as path
    print(f"Running " , path.abspath(__file__) , '...')
    import get_init_mkvs_for_manual_edits
    get_init_mkvs_for_manual_edits.main()
    print("End of Main") 